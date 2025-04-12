import os
import psycopg2
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create a connection to the PostgreSQL database"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
            
        result = urlparse(database_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        
        connection = psycopg2.connect(
            host=hostname,
            database=database,
            user=username,
            password=password,
            port=port
        )
        return connection
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise

def init_database():
    """Initialize the database with schema and sample data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create table
        with open('create_company_table.sql', 'r') as f:
            cursor.execute(f.read())
        
        # Insert sample data
        sample_data = [
            ('Apple Inc.', 'USA', '334111', 394.33, 2800.00, 15.2, 8.1),
            ('Samsung Electronics', 'South Korea', '334111', 245.00, 350.00, 12.5, 5.8),
            ('Microsoft', 'USA', '511210', 198.27, 2500.00, 18.3, 7.9),
            ('Amazon', 'USA', '454110', 513.98, 1700.00, 14.7, 9.2),
            ('Tesla', 'USA', '336111', 81.46, 800.00, 3.2, 12.5),
            ('Intel', 'USA', '334413', 77.87, 200.00, 8.9, 4.3),
            ('Siemens', 'Germany', '333611', 78.00, 120.00, 6.5, 3.8),
            ('General Electric', 'USA', '333611', 76.56, 100.00, 5.8, 2.9),
            ('Boeing', 'USA', '336411', 66.61, 120.00, 4.2, -3.5),
            ('Lockheed Martin', 'USA', '336414', 65.98, 110.00, 3.8, 4.1)
        ]
        
        cursor.executemany("""
            INSERT INTO top_global_firms 
            (company_name, country, naics_codes, revenue, market_cap, market_share, yoy_growth)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, sample_data)
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    init_database() 