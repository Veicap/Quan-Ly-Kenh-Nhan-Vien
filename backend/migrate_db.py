import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'db.sqlite3')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Add employee_id to gmail_accounts if it doesn't exist
    try:
        cursor.execute("ALTER TABLE gmail_accounts ADD COLUMN employee_id INTEGER REFERENCES users(id)")
        print("Added employee_id to gmail_accounts.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column employee_id already exists.")
        else:
            print("Error adding column:", e)

    # 2. Add status to youtube_channels if it doesn't exist
    try:
        cursor.execute("ALTER TABLE youtube_channels ADD COLUMN status VARCHAR(20) DEFAULT 'active'")
        print("Added status to youtube_channels.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column status already exists.")
        else:
            print("Error adding column status:", e)

    # 3. Create system_notifications table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type VARCHAR(50) NOT NULL,
        message VARCHAR(500) NOT NULL,
        is_read BOOLEAN DEFAULT 0,
        related_channel_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print("Checked system_notifications table.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    migrate()
