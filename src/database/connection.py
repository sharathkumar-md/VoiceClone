"""
SQLite Database Connection and Initialization
"""
import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Database file location
DB_PATH = Path(__file__).parents[2] / "data" / "stories.db"


def get_db():
    """Get database connection"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def init_db():
    """Initialize database schema"""
    conn = get_db()
    cursor = conn.cursor()

    # Create stories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stories (
            id TEXT PRIMARY KEY,
            title TEXT,
            text TEXT NOT NULL,
            theme TEXT NOT NULL,
            style TEXT NOT NULL,
            tone TEXT NOT NULL,
            length TEXT NOT NULL,
            word_count INTEGER NOT NULL,
            thumbnail_color TEXT,
            preview_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            audio_url TEXT,
            metadata TEXT
        )
    """)

    # Create index for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_created_at
        ON stories(created_at DESC)
    """)

    conn.commit()
    conn.close()

    logger.info(f"Database initialized at: {DB_PATH}")


if __name__ == "__main__":
    init_db()
    print(f"✅ Database initialized successfully at: {DB_PATH}")
