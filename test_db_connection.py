import os
import psycopg2
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    """Test the database connection and verify table setup"""
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            return False
            
        logger.info("Testing database connection...")
        
        # Parse the database URL
        result = urlparse(database_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        
        # Try to connect
        conn = psycopg2.connect(
            host=hostname,
            database=database,
            user=username,
            password=password,
            port=port
        )
        logger.info("Successfully connected to database!")
        
        # Check if table exists
        cursor = conn.cursor()
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'top_global_firms'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            logger.info("Table 'top_global_firms' exists")
            
            # Count records
            cursor.execute("SELECT COUNT(*) FROM top_global_firms")
            count = cursor.fetchone()[0]
            logger.info(f"Found {count} records in the table")
            
            # Show sample data
            cursor.execute("SELECT company_name, naics_codes FROM top_global_firms LIMIT 5")
            logger.info("Sample data:")
            for row in cursor.fetchall():
                logger.info(f"Company: {row[0]}, NAICS: {row[1]}")
        else:
            logger.warning("Table 'top_global_firms' does not exist")
            
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error testing database connection: {e}")
        return False

if __name__ == "__main__":
    test_connection() 