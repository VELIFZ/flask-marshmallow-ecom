from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy import select, or_, and_, desc, insert, update, delete
from models import db
from models.review_model import Review
from models.user_model import User
from models.book_model import Book
from schemas.review_schema import review_schema, reviews_schema
from routes.auth_routes import token_required
from utils.db_helpers import (
    get_table, row_to_dict, rows_to_list, paginate_results,
    handle_error, execute_query, get_by_id
)
from datetime import datetime

review_bp = Blueprint('review', __name__)

@review_bp.route('/reviews', methods=['POST'])
# @token_required - Temporarily removed for testing
def create_review():
    try:
        data = request.json
        
        # For testing, use buyer_id from request instead of from token
        if 'buyer_id' not in data:
            return jsonify({"error": "buyer_id is required"}), 400
        
        # Get tables
        users_table = get_table('users')
        reviews_table = get_table('reviews')
        books_table = get_table('books')
        
        # Validate seller exists
        seller_query = select(users_table).where(users_table.c.id == data['seller_id'])
        seller = execute_query(seller_query, single_result=True)
        if not seller:
            return jsonify({"error": "Seller not found"}), 404
        
        # If book_id is provided, validate book exists
        if 'book_id' in data and data['book_id']:
            book_query = select(books_table).where(books_table.c.id == data['book_id'])
            book = execute_query(book_query, single_result=True)
            if not book:
                return jsonify({"error": "Book not found"}), 404
                
            # Verify that the book belongs to the seller
            if book.seller_id != seller.id:
                return jsonify({"error": "Book does not belong to specified seller"}), 400
        
        # Prevent users from reviewing themselves
        if data['buyer_id'] == data['seller_id']:
            return jsonify({"error": "You cannot review yourself"}), 400
            
        # Validate no duplicate reviews from same buyer to same seller
        existing_query = select(reviews_table).where(
            (reviews_table.c.buyer_id == data['buyer_id']) & 
            (reviews_table.c.seller_id == data['seller_id'])
        )
        existing_review = execute_query(existing_query, single_result=True)
        
        if existing_review:
            return jsonify({"error": "You have already reviewed this seller"}), 409
            
        # Add created_at timestamp
        data['created_at'] = datetime.utcnow()
            
        # Create review using direct SQL
        stmt = insert(reviews_table).values(**data)
        result = db.session.execute(stmt)
        
        # Get the new review ID
        review_id = result.inserted_primary_key[0]
        
        # Update seller rating
        seller_reviews_query = select(reviews_table).where(reviews_table.c.seller_id == data['seller_id'])
        seller_reviews = execute_query(seller_reviews_query)
        
        if seller_reviews:
            total_rating = sum(review.rating for review in seller_reviews) + data['rating']
            avg_rating = total_rating / (len(seller_reviews) + 1)
            
            # Update seller rating
            update_stmt = update(users_table).where(
                users_table.c.id == data['seller_id']
            ).values(
                rating=avg_rating
            )
            db.session.execute(update_stmt)
        
        db.session.commit()
        
        # Get the created review
        new_review_query = select(reviews_table).where(reviews_table.c.id == review_id)
        new_review = execute_query(new_review_query, single_result=True)
        review_dict = row_to_dict(new_review, reviews_table)
        
        return jsonify({
            "message": "Review created successfully",
            "review": review_dict
        }), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return handle_error(e, "creating review")

@review_bp.route('/reviews', methods=['GET'])
def get_reviews():
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Get reviews table
        reviews_table = get_table('reviews')
        
        # Build query
        query = select(reviews_table)
        
        # Execute query
        reviews = execute_query(query)
        
        # Convert to list of dictionaries
        review_list = rows_to_list(reviews, reviews_table)
        
        # Paginate results
        paginated_reviews = paginate_results(review_list, page, limit)
        
        return jsonify({
            "page": page, 
            "total": len(review_list),
            "reviews": paginated_reviews
        }), 200
    except Exception as e:
        return handle_error(e, "getting reviews")

@review_bp.route('/review/<int:id>', methods=['GET'])
def get_review(id):
    # Simply use our helper function
    return get_by_id('reviews', id)

@review_bp.route('/review/<int:id>', methods=['PUT'])
# @token_required - Temporarily removed for testing
def update_review(id):
    try:
        # Get tables
        reviews_table = get_table('reviews')
        users_table = get_table('users')
        
        # First check if the review exists
        result, _ = get_by_id('reviews', id, response=False)
        
        if not result:
            return jsonify({"error": "Review not found"}), 404
            
        # Authentication check removed for testing
        # if result.buyer_id != current_user.id:
        #     return jsonify({"error": "Unauthorized to update this review"}), 403
            
        data = request.json
        old_rating = result.rating
        
        # Prepare update data
        update_data = {}
        for key, value in data.items():
            # Prevent changing buyer_id or seller_id
            if key not in ['buyer_id', 'seller_id'] and hasattr(reviews_table.c, key):
                update_data[key] = value
        
        # Update the review
        stmt = update(reviews_table).where(reviews_table.c.id == id).values(**update_data)
        db.session.execute(stmt)
        
        # If rating changed, update seller's average rating
        if 'rating' in data and data['rating'] != old_rating:
            # Get all reviews for the seller
            seller_id = result.seller_id
            seller_reviews_query = select(reviews_table).where(reviews_table.c.seller_id == seller_id)
            seller_reviews = execute_query(seller_reviews_query)
            
            if seller_reviews:
                # Calculate new average rating
                total_rating = sum(r.rating for r in seller_reviews)
                avg_rating = total_rating / len(seller_reviews)
                
                # Update seller rating
                update_seller_stmt = update(users_table).where(
                    users_table.c.id == seller_id
                ).values(
                    rating=avg_rating
                )
                db.session.execute(update_seller_stmt)
            
        db.session.commit()
        
        # Get the updated review
        return get_by_id('reviews', id)
        
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return handle_error(e, "updating review")

@review_bp.route('/review/<int:id>', methods=['DELETE'])
# @token_required - Temporarily removed for testing
def delete_review(id):
    try:
        # Get tables
        reviews_table = get_table('reviews')
        users_table = get_table('users')
        
        # First check if the review exists
        result, _ = get_by_id('reviews', id, response=False)
        
        if not result:
            return jsonify({"error": "Review not found"}), 404
            
        # Authentication check removed for testing
        # if result.buyer_id != current_user.id:
        #     return jsonify({"error": "Unauthorized to delete this review"}), 403
            
        seller_id = result.seller_id
        
        # Delete the review
        delete_stmt = delete(reviews_table).where(reviews_table.c.id == id)
        db.session.execute(delete_stmt)
        
        # Update seller rating
        seller_reviews_query = select(reviews_table).where(reviews_table.c.seller_id == seller_id)
        seller_reviews = execute_query(seller_reviews_query)
        
        if seller_reviews:
            # Calculate new average rating
            total_rating = sum(r.rating for r in seller_reviews)
            avg_rating = total_rating / len(seller_reviews)
            
            # Update seller rating
            update_seller_stmt = update(users_table).where(
                users_table.c.id == seller_id
            ).values(
                rating=avg_rating
            )
            db.session.execute(update_seller_stmt)
        else:
            # No reviews left, reset to default rating of 0
            update_seller_stmt = update(users_table).where(
                users_table.c.id == seller_id
            ).values(
                rating=0
            )
            db.session.execute(update_seller_stmt)
            
        db.session.commit()
        
        return jsonify({"message": "Review deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return handle_error(e, "deleting review")

@review_bp.route('/users/<int:id>/reviews', methods=['GET'])
def get_user_reviews(id):
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        type_filter = request.args.get('type', 'buyer')  # 'buyer' or 'seller'
        
        reviews_table = get_table('reviews')
        users_table = get_table('users')
        
        # Check if user exists
        user_query = select(users_table).where(users_table.c.id == id)
        user = execute_query(user_query, single_result=True)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Build query based on type filter
        if type_filter == 'buyer':
            query = select(reviews_table).where(reviews_table.c.buyer_id == id)
        else:
            query = select(reviews_table).where(reviews_table.c.seller_id == id)
        
        # Execute query
        reviews = execute_query(query)
        review_list = rows_to_list(reviews, reviews_table)
        
        # Apply pagination
        paginated_reviews = paginate_results(review_list, page, limit)
        
        return jsonify({
            "page": page,
            "per_page": limit,
            "total": len(review_list),
            "reviews": paginated_reviews
        }), 200
        
    except Exception as e:
        return handle_error(e, "fetching user reviews")

@review_bp.route('/books/<int:id>/reviews', methods=['GET'])
def get_book_reviews(id):
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Check if book exists
        books_table = get_table('books')
        book_query = select(books_table).where(books_table.c.id == id)
        book = execute_query(book_query, single_result=True)
        
        if not book:
            return jsonify({"error": "Book not found"}), 404
            
        # Get reviews table
        reviews_table = get_table('reviews')
        
        # Query for reviews for this book
        query = select(reviews_table).where(reviews_table.c.book_id == id)
            
        # Execute query
        reviews = execute_query(query)
        
        # Convert to list of dictionaries
        review_list = rows_to_list(reviews, reviews_table)
        
        # Paginate results
        paginated_reviews = paginate_results(review_list, page, limit)
        
        # For each review, get the buyer details
        users_table = get_table('users')
        for review_dict in paginated_reviews:
            # Get buyer info
            buyer_query = select(users_table).where(users_table.c.id == review_dict['buyer_id'])
            buyer = execute_query(buyer_query, single_result=True)
            if buyer:
                review_dict['buyer'] = row_to_dict(buyer, users_table)
        
        return jsonify({
            "page": page,
            "total": len(review_list),
            "reviews": paginated_reviews
        }), 200
    except Exception as e:
        return handle_error(e, f"getting reviews for book {id}") 