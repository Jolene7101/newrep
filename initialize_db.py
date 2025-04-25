"""
Database Initialization Script for FireproofAI Lead Generation System

This script creates a fresh database with the correct schema if none exists.
"""
import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = "db/filters.db"

def initialize_database():
    """Initialize the database with the new schema if it doesn't exist."""
    # Check if database directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Check if database file exists
    db_exists = os.path.exists(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        if not db_exists:
            logger.info(f"Creating new database at {DB_PATH}")
            
            # Create the filters table with the new schema
            cursor.execute("""
            CREATE TABLE filters (
                email TEXT PRIMARY KEY,
                states TEXT,
                keywords TEXT,
                source_gc INTEGER,
                source_linkedin INTEGER,
                source_twitter INTEGER,
                source_google_news INTEGER,
                source_reddit INTEGER,
                proxy TEXT
            )
            """)
            
            # Add a test user
            cursor.execute("""
            INSERT INTO filters (email, states, keywords, source_gc, source_linkedin, source_twitter, 
                               source_google_news, source_reddit, proxy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("test@example.com", "TX,CA,NY", "data center, fireproofing, steel", 
                  1, 1, 1, 1, 1, ""))
            
            conn.commit()
            logger.info("Database initialized with test user")
            return True
        else:
            # Check if we have the correct schema
            cursor.execute("PRAGMA table_info(filters)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if "states" in columns:
                logger.info("Database already exists with correct schema")
                return True
            else:
                logger.warning("Database exists but has old schema. Use db_migration.py to migrate.")
                return False
    except Exception as e:
        conn.rollback()
        logger.error(f"Database initialization failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("Starting database initialization")
    success = initialize_database()
    if success:
        logger.info("Database initialization completed successfully")
    else:
        logger.error("Database initialization failed")
