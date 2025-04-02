"""
Database helper functions to simplify SQL operations and standardize error handling
"""
from flask import jsonify
from sqlalchemy import Table, MetaData, select, insert
from models import db

def get_table(table_name):
    """Create a SQLAlchemy Table object with autoload"""
    metadata = MetaData()
    return Table(table_name, metadata, autoload_with=db.engine)

def row_to_dict(row, table):
    """Convert a SQLAlchemy result row to a dictionary"""
    if not row:
        return None
    result = {}
    for column in table.columns:
        result[column.name] = getattr(row, column.name)
    return result

def rows_to_list(rows, table):
    """Convert multiple SQLAlchemy result rows to a list of dictionaries"""
    return [row_to_dict(row, table) for row in rows]

def paginate_results(results, page, limit):
    """Paginate a list of results"""
    start = (page - 1) * limit
    end = start + limit
    return results[start:end] if start < len(results) else []

def handle_error(e, operation="database operation"):
    """Handle exceptions with consistent logging and response format"""
    db.session.rollback()
    print(f"Error during {operation}: {str(e)}")
    return jsonify({"error": str(e)}), 500

def execute_query(query, single_result=False):
    """Execute a query and handle errors consistently"""
    try:
        result = db.session.execute(query)
        if single_result:
            return result.first()
        return result.fetchall()
    except Exception as e:
        return handle_error(e, "query execution")

def get_by_id(table_name, id, response=True):
    """Get a record by ID with standard error handling"""
    try:
        table = get_table(table_name)
        query = select(table).where(table.c.id == id)
        result = db.session.execute(query).first()
        
        if not result:
            if response:
                return jsonify({"error": f"{table_name.title()} not found"}), 404
            return None
            
        if response:
            return jsonify(row_to_dict(result, table)), 200
        return result, table
        
    except Exception as e:
        if response:
            return handle_error(e, f"getting {table_name} by ID")
        raise e 

def create_record(table_name, data):
    """Create a new record in the specified table"""
    try:
        # Get table
        table = get_table(table_name)
        
        # Insert the record
        stmt = insert(table).values(**data)
        result = db.session.execute(stmt)
        db.session.commit()
        
        # Get the new record ID
        record_id = result.inserted_primary_key[0] if result.inserted_primary_key else None
        
        # Return success response
        data['id'] = record_id
        return jsonify({
            "message": f"{table_name.title()} created successfully",
            table_name: data
        }), 201
        
    except Exception as e:
        return handle_error(e, f"creating {table_name}") 