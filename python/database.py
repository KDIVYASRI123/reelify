import sqlite3
import os

def init_database(db_path: str = "app_database.db"):
    """Initialize the application database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Video processing history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processing_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            original_filename TEXT,
            processing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reels_generated INTEGER,
            status TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Reels table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            processing_id INTEGER,
            reel_path TEXT,
            duration INTEGER,
            segment_text TEXT,
            start_time REAL,
            end_time REAL,
            FOREIGN KEY (processing_id) REFERENCES processing_history (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()
