import sqlite3
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

DATABASE_PATH = 'taxonomy.db'

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def get_all_categories():
    """Get all top-level categories"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT category 
            FROM taxonomy 
            WHERE category != ''
            ORDER BY category
        """)
        return cursor.fetchall()

def get_subcategories(category):
    """Get subcategories for a given category"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM taxonomy 
            WHERE category = ? AND subcategory != ''
            GROUP BY subcategory
            ORDER BY subcategory
        """, (category,))
        return cursor.fetchall()

def get_sub_subcategories(category, subcategory):
    """Get sub-subcategories for a given subcategory"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM taxonomy 
            WHERE category = ? 
            AND subcategory = ?
            AND sub_subcategory IS NOT NULL
            AND sub_subcategory != ''
            ORDER BY sub_subcategory
        """, (category, subcategory))
        return cursor.fetchall()

def filter_taxonomy(filters, filter_mode="AND"):
    """
    Filter taxonomy data based on provided filters
    
    Args:
        filters (dict): Dictionary of filters {field: value}
        filter_mode (str): "AND" or "OR" for filter combination
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_clauses = []
        params = []
        for field, value in filters.items():
            where_clauses.append(f"{field} = ?")
            params.append(value)
            
        # Combine clauses based on filter mode
        where_sql = " AND " if filter_mode == "AND" else " OR "
        where_sql = where_sql.join(where_clauses)
        
        query = f"""
            SELECT DISTINCT category, subcategory, naics_code, naics_description,
                   sub_subcategory, sub_naics_code, sub_naics_description,
                   function, supply_chain_position, trl, potential_applications
            FROM taxonomy
            WHERE {where_sql}
            ORDER BY category, subcategory, sub_subcategory
        """
        
        cursor.execute(query, params)
        return cursor.fetchall()

def get_distinct_values(field):
    """Get distinct values for a given field"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT DISTINCT {field}
            FROM taxonomy
            WHERE {field} IS NOT NULL
            ORDER BY {field}
        """)
        return [row[0] for row in cursor.fetchall()]

def init_database():
    """Initialize the database and create the taxonomy table"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS taxonomy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                naics_code TEXT,
                naics_description TEXT,
                sub_subcategory TEXT,
                sub_naics_code TEXT,
                sub_naics_description TEXT,
                function TEXT,
                supply_chain_position TEXT,
                trl TEXT,
                potential_applications TEXT
            )
        """)
        conn.commit()

def import_json_to_db(json_file_path):
    """Import data from JSON file into the database"""
    import json
    
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM taxonomy")
        
        # Insert new data
        for item in data:
            cursor.execute("""
                INSERT INTO taxonomy (
                    category, subcategory, naics_code, naics_description,
                    sub_subcategory, sub_naics_code, sub_naics_description,
                    function, supply_chain_position, trl, potential_applications
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item['Category'],
                item['Subcategory'],
                str(item['NAICS Code']),
                item['NAICS Description'],
                item['Potential Sub-Subcategory'] if item['Potential Sub-Subcategory'] != 'N/A' else None,
                item['Sub-Subcategory NAICS Code'] if item['Sub-Subcategory NAICS Code'] != 'N/A' else None,
                item['Sub-Subcategory NAICS Description'] if item['Sub-Subcategory NAICS Description'] != 'N/A' else None,
                item.get('Function'),
                item.get('Supply Chain Position'),
                item.get('TRL'),
                item.get('Potential Applications')
            ))
        
        conn.commit()

def get_table_schema():
    """Print the current table schema"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sql 
            FROM sqlite_master 
            WHERE type='table' AND name='taxonomy';
        """)
        print("Current table schema:")
        print(cursor.fetchone()[0])

def get_sample_data():
    """Print a sample row from the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM taxonomy LIMIT 1")
        columns = [description[0] for description in cursor.description]
        row = cursor.fetchone()
        print("\nColumns:", columns)
        print("Sample data:", dict(zip(columns, row)))

def verify_database():
    """Verify database structure and sample data"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check table structure
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='taxonomy'
        """)
        print("Table structure:", cursor.fetchone()[0])
        
        # Check sample data
        cursor.execute("""
            SELECT * FROM taxonomy 
            WHERE sub_subcategory IS NOT NULL 
            LIMIT 1
        """)
        row = cursor.fetchone()
        print("\nSample row with sub-subcategory:", dict(row) if row else "No sub-subcategories found")
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM taxonomy")
        print("\nTotal records:", cursor.fetchone()[0])
        
        # Count sub-subcategories
        cursor.execute("SELECT COUNT(*) FROM taxonomy WHERE sub_subcategory IS NOT NULL")
        print("Records with sub-subcategories:", cursor.fetchone()[0])

# Add this at the end of the file
if __name__ == "__main__":
    # Initialize the database
    init_database()
    
    # Import data from JSON
    import_json_to_db('tax_5-1.json')
    logger.info("Database initialized and data imported successfully")
    
    get_table_schema()
    get_sample_data()
    
    verify_database() 