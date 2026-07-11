import os
import mysql.connector
from mysql.connector import pooling

db_config = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "mukesh@790107"),
    "database": os.environ.get("DB_DATABASE", "traffic_db"),
    "port": int(os.environ.get("DB_PORT", 3306))
}

# Create a connection pool for optimized multi-threaded performance
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="traffic_pool",
        pool_size=10,
        pool_reset_session=True,
        **db_config
    )
    print("Database connection pool initialized successfully!")
except Exception as e:
    print(f"Error creating connection pool: {e}. Falling back to standard connections.")
    connection_pool = None

def get_db_connection():
    """
    Returns a database connection from the pool, or creates a new one as a fallback.
    """
    if connection_pool:
        try:
            return connection_pool.get_connection()
        except Exception as e:
            print(f"Failed to get pooled connection: {e}. Retrying with direct connection...")
    
    return mysql.connector.connect(**db_config)
