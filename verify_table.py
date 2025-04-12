import os
import psycopg2
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_table():
    """Verify the table structure in the database"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            return False
            
        logger.info(f"Using database URL: {database_url}")
        
        result = urlparse(database_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        
        conn = psycopg2.connect(
            host=hostname,
            database=database,
            user=username,
            password=password,
            port=port
        )
        logger.info("Connected to database")
        
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'top_global_firms'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            logger.info("Table 'top_global_firms' exists")
            
            # Get table structure
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'top_global_firms'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            logger.info("Table structure:")
            for column in columns:
                logger.info(f"Column: {column[0]}, Type: {column[1]}")
            
            # Count records
            cursor.execute("SELECT COUNT(*) FROM top_global_firms")
            count = cursor.fetchone()[0]
            logger.info(f"Total records: {count}")
            
            # Show sample data
            cursor.execute("SELECT * FROM top_global_firms LIMIT 1")
            sample = cursor.fetchone()
            if sample:
                logger.info("Sample record:")
                logger.info(sample)
        else:
            logger.error("Table 'top_global_firms' does not exist")
            
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error verifying table: {str(e)}")
        return False

if __name__ == "__main__":
    verify_table() 