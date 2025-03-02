import sqlite3
from contextlib import contextmanager
import logging
import os
import json
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use /tmp directory for Render deployment
DATABASE_PATH = '/tmp/taxonomy.db'

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        # Create a data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Connect to SQLite database (will create if not exists)
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
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
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create taxonomy table with correct schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS taxonomy (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Category TEXT,
                    Subcategory TEXT,
                    "NAICS Code" INTEGER,
                    "NAICS Description" TEXT,
                    "Potential Sub-Subcategory" TEXT,
                    "Sub-Subcategory NAICS Code" TEXT,
                    "Sub-Subcategory NAICS Description" TEXT,
                    "Potential Applications" TEXT,
                    "Function" TEXT,
                    "Supply Chain Position" TEXT,
                    "TRL" TEXT
                )
            ''')
            
            # Create top_global_firms table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS top_global_firms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Company_Name TEXT,
                    Country TEXT,
                    Revenue REAL,
                    Market_Cap REAL,
                    YoY_Growth REAL,
                    Description TEXT,
                    NAICS_Codes TEXT,
                    Market_Share REAL,
                    Patents_Last_Year INTEGER,
                    R_and_D_Spending_Percentage REAL
                )
            ''')
            
            conn.commit()
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def import_json_to_db(json_file_path):
    """Import data from a JSON file into the database."""
    try:
        # Try the direct path first
        if not os.path.exists(json_file_path):
            # Try looking in the data directory relative to the current file
            alt_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'taxonomy.json')
            if os.path.exists(alt_path):
                json_file_path = alt_path
            else:
                raise FileNotFoundError(f"Could not find taxonomy.json in {json_file_path} or {alt_path}")

        with open(json_file_path, 'r') as file:
            data = json.load(file)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute('DELETE FROM taxonomy')
            
            # Insert new data
            for item in data:
                cursor.execute('''
                    INSERT INTO taxonomy (
                        Category, Subcategory, "NAICS Code", "NAICS Description",
                        "Potential Sub-Subcategory", "Sub-Subcategory NAICS Code",
                        "Sub-Subcategory NAICS Description", "Potential Applications",
                        "Function", "Supply Chain Position", "TRL"
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('Category'),
                    item.get('Subcategory'),
                    item.get('NAICS Code'),
                    item.get('NAICS Description'),
                    item.get('Potential Sub-Subcategory'),
                    item.get('Sub-Subcategory NAICS Code'),
                    item.get('Sub-Subcategory NAICS Description'),
                    item.get('Potential Applications'),
                    item.get('Function'),
                    item.get('Supply Chain Position'),
                    item.get('TRL')
                ))
            
            conn.commit()
            logger.info(f"Successfully imported taxonomy data from {json_file_path}")
    except Exception as e:
        logger.error(f"Error importing taxonomy data: {e}")
        raise

def import_companies_to_db(json_file_path):
    """Import company data from JSON file into the database"""
    try:
        # Try the direct path first
        if not os.path.exists(json_file_path):
            # Try looking in the root directory
            alt_path = os.path.join(os.path.dirname(__file__), '..', 'top_global_firms.json')
            if os.path.exists(alt_path):
                json_file_path = alt_path
            else:
                raise FileNotFoundError(f"Could not find top_global_firms.json in {json_file_path} or {alt_path}")

        with open(json_file_path, 'r') as file:
            data = json.load(file)

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM top_global_firms')
        
        # Insert new data
        for company in data:
            cursor.execute('''
                INSERT INTO top_global_firms (
                    Company_Name, Country, Revenue, Market_Cap, YoY_Growth,
                    Description, NAICS_Codes, Market_Share, Patents_Last_Year,
                    R_and_D_Spending_Percentage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company.get('Company_Name'),
                company.get('Country'),
                company.get('Revenue'),
                company.get('Market_Cap'),
                company.get('YoY_Growth'),
                company.get('Description'),
                company.get('NAICS_Codes'),
                company.get('Market_Share'),
                company.get('Patents_Last_Year'),
                company.get('R&D_Spending_Percentage')
            ))
        
        conn.commit()
        logger.info(f"Successfully imported company data from {json_file_path}")
    except (sqlite3.Error, json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error importing company data: {e}")
        raise
    finally:
        conn.close()

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