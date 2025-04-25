"""
Database Migration Utility for FireproofAI Lead Generation System

This script handles the migration from the old database schema (using valuation_min and min_stories)
to the new schema using states filtering.
"""
import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = "db/filters.db"
BACKUP_PATH = "db/filters_backup.db"

def backup_database():
    """Create a backup of the existing database before migration."""
    if not os.path.exists(DB_PATH):
        logger.warning(f"No database found at {DB_PATH}, nothing to backup")
        return False
    
    import shutil
    try:
        shutil.copy(DB_PATH, BACKUP_PATH)
        logger.info(f"Database backup created at {BACKUP_PATH}")
        return True
    except Exception as e:
        logger.error(f"Failed to create database backup: {e}")
        return False

def migrate_database():
    """Migrate the database to the new schema with states field."""
    if not os.path.exists(DB_PATH):
        logger.warning(f"No database found at {DB_PATH}, nothing to migrate")
        return False
    
    # First, create a backup
    if not backup_database():
        logger.error("Aborting migration due to backup failure")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if the old schema exists
        cursor.execute("PRAGMA table_info(filters)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if "valuation_min" in columns and "min_stories" in columns and "states" not in columns:
            logger.info("Beginning migration from old schema to new schema")
            
            # Get existing data
            cursor.execute("SELECT * FROM filters")
            old_data = cursor.fetchall()
            
            # Create new table with temporary name
            cursor.execute("""
            CREATE TABLE filters_new (
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
            
            # Insert data with default state values (TX,CA,NY)
            for row in old_data:
                email = row[0]
                keywords = row[3] if len(row) > 3 else ""
                source_gc = row[4] if len(row) > 4 else 1
                source_linkedin = row[5] if len(row) > 5 else 1
                source_twitter = row[6] if len(row) > 6 else 1
                source_google_news = row[7] if len(row) > 7 else 1
                source_reddit = row[8] if len(row) > 8 else 1
                proxy = row[9] if len(row) > 9 else ""
                
                cursor.execute("""
                INSERT INTO filters_new VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (email, "TX,CA,NY", keywords, source_gc, source_linkedin, 
                      source_twitter, source_google_news, source_reddit, proxy))
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE filters")
            cursor.execute("ALTER TABLE filters_new RENAME TO filters")
            
            conn.commit()
            logger.info("Migration completed successfully")
            return True
            
        elif "states" in columns:
            logger.info("Database already using new schema with states field")
            return True
        else:
            logger.warning("Unexpected database schema")
            return False
            
    except Exception as e:
        conn.rollback()
        logger.error(f"Migration failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("Starting database migration")
    success = migrate_database()
    if success:
        logger.info("Migration completed successfully")
    else:
        logger.error("Migration failed")
