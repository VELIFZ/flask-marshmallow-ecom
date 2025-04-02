from flask import request, jsonify, Blueprint, current_app
from marshmallow import ValidationError
from sqlalchemy import select, or_, and_, desc, text, update, delete
from schemas.book_schema import book_schema, books_schema
from models import db
from models.book_model import Book
from sqlalchemy.orm import selectinload
from werkzeug.utils import secure_filename
from routes.auth_routes import token_required
import os
import uuid
from sqlalchemy import Table, Column, MetaData, insert
from utils.db_helpers import (
    get_table, row_to_dict, rows_to_list, paginate_results, 
    handle_error, execute_query, get_by_id, create_record
)

book_bp = Blueprint('book', __name__)

@book_bp.route('/books', methods=['POST'])
# @token_required  # Temporarily commented out for development
def create_book():  # Removed current_user parameter
    try:
        # Get book data from request
        book_data = request.json
        
        # Use seller_id from request if provided, otherwise default to 1
        if 'seller_id' not in book_data:
            book_data['seller_id'] = 1  # Default seller ID if not specified
            
        book_data['status'] = 'Available'  # Default status - Note: Capitalized to match Enum
        
        # Debug: print what we're trying to create
        print(f"Attempting to create book with data: {book_data}")
        
        # Prepare insert data - only include fields that are provided
        insert_data = {
            'title': book_data.get('title'),
            'author': book_data.get('author'),
            'price': book_data.get('price'),
            'seller_id': book_data.get('seller_id', 1),
            'status': book_data.get('status', 'Available')
        }
        
        # Add optional fields if they exist
        if 'description' in book_data:
            insert_data['description'] = book_data['description']
        if 'condition' in book_data:
            insert_data['condition'] = book_data['condition']
        if 'genre' in book_data:
            insert_data['genre'] = book_data['genre']
        if 'publication_year' in book_data:
            insert_data['publication_year'] = book_data['publication_year']
        if 'isbn' in book_data:
            insert_data['isbn'] = book_data['isbn']
        if 'image_url' in book_data:
            insert_data['image_url'] = book_data['image_url']
            
        # Create the book using our helper function
        return create_record('books', insert_data)
            
    except ValidationError as err:
        print(f"Validation error: {err.messages}")
        return jsonify(err.messages), 400
    except Exception as e:
        return handle_error(e, "creating book")

@book_bp.route('/books', methods=['GET'])
def get_books():
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        search = request.args.get('search', type=str)
        
        # Get books table
        books_table = get_table('books')
        
        # Build the query using SQLAlchemy Core
        query = select(books_table)
        
        # Add search functionality if requested
        if search:
            query = query.where(
                or_(
                    books_table.c.title.ilike(f'%{search}%'),
                    books_table.c.author.ilike(f'%{search}%'),
                    books_table.c.genre.ilike(f'%{search}%')
                )
            )
        
        # Execute the query and get results
        books = execute_query(query)
        
        # Convert to a list of dictionaries
        book_list = rows_to_list(books, books_table)
        
        # Paginate results
        paginated_books = paginate_results(book_list, page, limit)
        
        return jsonify({
            "page": page,
            "total": len(book_list),
            "books": paginated_books
        }), 200
        
    except Exception as e:
        return handle_error(e, "listing books")

@book_bp.route('/books/search', methods=['GET'])
def search_books():
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        search_term = request.args.get('q', type=str)
        
        # Filtering parameters
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        genre = request.args.get('genre', type=str)
        condition = request.args.get('condition', type=str)
        author = request.args.get('author', type=str)
        min_year = request.args.get('min_year', type=int)
        max_year = request.args.get('max_year', type=int)
        status = request.args.get('status', type=str)
        
        # Sorting parameters
        sort_by = request.args.get('sort_by', 'id')  # Default to id instead of created_at
        sort_order = request.args.get('sort_order', 'desc')
        
        # Get books table
        books_table = get_table('books')
        
        # Build the query using SQLAlchemy Core
        query = select(books_table)
        
        # Apply text search
        if search_term:
            search_filter = or_(
                books_table.c.title.ilike(f'%{search_term}%'),
                books_table.c.author.ilike(f'%{search_term}%'),
                books_table.c.description.ilike(f'%{search_term}%'),
                books_table.c.genre.ilike(f'%{search_term}%')
            )
            query = query.where(search_filter)
        
        # Apply filters
        if min_price is not None:
            query = query.where(books_table.c.price >= min_price)
            
        if max_price is not None:
            query = query.where(books_table.c.price <= max_price)
            
        if genre:
            query = query.where(books_table.c.genre.ilike(f'%{genre}%'))
            
        if condition:
            query = query.where(books_table.c.condition == condition)
            
        if author:
            query = query.where(books_table.c.author.ilike(f'%{author}%'))
            
        if min_year is not None:
            query = query.where(books_table.c.publication_year >= min_year)
            
        if max_year is not None:
            query = query.where(books_table.c.publication_year <= max_year)
            
        if status:
            query = query.where(books_table.c.status == status)
        
        # Apply sorting - check if the sort column exists in the table
        if hasattr(books_table.c, sort_by):
            sort_column = getattr(books_table.c, sort_by)
        else:
            # Fallback to id if the requested sort column doesn't exist
            sort_column = books_table.c.id
            
        if sort_order == 'desc':
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)
        
        # Execute query 
        books = execute_query(query)
        
        # Convert to a list of dictionaries
        book_list = rows_to_list(books, books_table)
        
        # Apply pagination
        paginated_books = paginate_results(book_list, page, limit)
        
        return jsonify({
            "page": page,
            "total": len(book_list),
            "books": paginated_books
        }), 200
        
    except Exception as e:
        return handle_error(e, "searching books")

@book_bp.route('/books/featured', methods=['GET'])
def get_featured_books():
    try:
        # Get query parameters
        limit = request.args.get('limit', 6, type=int)
        
        # Use direct SQL approach to avoid loading relationships
        from sqlalchemy import Table, MetaData, select, desc
        
        # Create the books table object
        metadata = MetaData()
        books_table = Table('books', metadata, autoload_with=db.engine)
        
        # Build the query for newest available books - use id instead of created_at
        query = select(books_table).where(
            books_table.c.status == 'Available'
        ).order_by(
            desc(books_table.c.id)  # Sort by ID descending to get newest
        ).limit(limit)
        
        # Execute the query
        result = db.session.execute(query)
        books = result.fetchall()
        
        # Convert to list of dictionaries
        featured_books = []
        for book in books:
            book_dict = {}
            for column in books_table.columns:
                book_dict[column.name] = getattr(book, column.name)
            featured_books.append(book_dict)
        
        return jsonify({
            "featured_books": featured_books
        }), 200
    except Exception as e:
        print(f"Error in get_featured_books: {str(e)}")
        return jsonify({"error": str(e)}), 500

@book_bp.route('/book/<int:id>', methods=['GET'])
def get_book(id):
    # Simply use our helper function
    return get_by_id('books', id)

@book_bp.route('/book/<int:id>', methods=['PUT'])
# @token_required
def update_book(id):
    try:
        books_table = get_table('books')
        
        # First check if the book exists
        result, table = get_by_id('books', id, response=False)
        
        if not result:
            return jsonify({"error": "Book not found"}), 404
        
        # Prepare update data from request
        update_data = {}
        for key, value in request.json.items():
            # Don't allow changing seller_id
            if key != 'seller_id' and hasattr(books_table.c, key):
                update_data[key] = value
        
        # Update the book
        stmt = update(books_table).where(books_table.c.id == id).values(**update_data)
        db.session.execute(stmt)
        db.session.commit()
        
        # Get the updated book
        return get_by_id('books', id)
        
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return handle_error(e, "updating book")

@book_bp.route('/book/<int:id>', methods=['DELETE'])
# @token_required
def delete_book(id):
    try:
        books_table = get_table('books')
        
        # First check if the book exists
        result, _ = get_by_id('books', id, response=False)
        
        if not result:
            return jsonify({"error": "Book not found"}), 404
        
        # Delete the book
        stmt = delete(books_table).where(books_table.c.id == id)
        db.session.execute(stmt)
        db.session.commit()
        
        return jsonify({"message": "Book deleted successfully"}), 200
    except Exception as e:
        return handle_error(e, "deleting book")

@book_bp.route('/book/<int:id>/upload-image', methods=['POST'])
@token_required
def upload_book_image(current_user, id):
    try:
        book = db.session.get(Book, id)
        if not book:
            return jsonify({"error": "Book not found"}), 404
            
        # Verify book belongs to the authenticated user
        if book.seller_id != current_user.id:
            return jsonify({"error": "Unauthorized to upload image for this book"}), 403
            
        # Check if the post request has the file part
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
            
        file = request.files['image']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if '.' not in file.filename or \
           file.filename.split('.')[-1].lower() not in allowed_extensions:
            return jsonify({"error": "File type not allowed"}), 400
            
        # Create a secure filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}-{filename}"
        
        # Ensure upload folder exists
        uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'books')
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(uploads_dir, unique_filename)
        file.save(file_path)
        
        # Update book image_url
        book.image_url = f"/static/uploads/books/{unique_filename}"
        db.session.commit()
        
        return jsonify({
            "message": "Image uploaded successfully",
            "image_url": book.image_url
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500