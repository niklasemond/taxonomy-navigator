import os
import psycopg2
from psycopg2 import Error
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_table():
    """Verify the table structure in the database"""
    try:
        # Get database URL from environment variable
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            return
            
        logger.info(f"Attempting to connect to database with URL: {database_url}")
        
        # Parse the database URL
        from urllib.parse import urlparse
        result = urlparse(database_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        
        # Connect to the database
        conn = psycopg2.connect(
            host=hostname,
            database=database,
            user=username,
            password=password,
            port=port,
            sslmode='require'
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'top_global_firms'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            logger.error("Table 'top_global_firms' does not exist")
            return
            
        # Get table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'top_global_firms';
        """)
        columns = cursor.fetchall()
        logger.info("Table structure:")
        for column in columns:
            logger.info(f"Column: {column[0]}, Type: {column[1]}")
            
        # Get record count
        cursor.execute("SELECT COUNT(*) FROM top_global_firms;")
        count = cursor.fetchone()[0]
        logger.info(f"Total records: {count}")
        
        # Get sample data
        cursor.execute("""
            SELECT * FROM top_global_firms 
            LIMIT 5;
        """)
        sample_data = cursor.fetchall()
        logger.info("Sample data:")
        for row in sample_data:
            logger.info(row)
            
        # Check specific NAICS code
        cursor.execute("""
            SELECT * FROM top_global_firms 
            WHERE NAICS_Codes LIKE '541%' 
            LIMIT 5;
        """)
        naics_data = cursor.fetchall()
        logger.info("Data for NAICS code 541:")
        for row in naics_data:
            logger.info(row)
            
        cursor.close()
        conn.close()
        
    except Error as e:
        logger.error(f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    verify_table() 