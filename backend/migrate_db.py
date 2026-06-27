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

    # 2. Add password and two_fa to gmail_accounts
    try:
        cursor.execute("ALTER TABLE gmail_accounts ADD COLUMN password VARCHAR(255) DEFAULT ''")
        cursor.execute("ALTER TABLE gmail_accounts ADD COLUMN two_fa VARCHAR(255) DEFAULT ''")
        print("Added password and two_fa to gmail_accounts.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Columns password/two_fa already exist.")
        else:
            print("Error adding columns:", e)

    # 3. Add status to youtube_channels if it doesn't exist
    try:
        cursor.execute("ALTER TABLE youtube_channels ADD COLUMN status VARCHAR(20) DEFAULT 'active'")
        print("Added status to youtube_channels.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column status already exists.")
        else:
            print("Error adding column status:", e)

    # 4. Add affiliate columns to youtube_channels
    try:
        cursor.execute("ALTER TABLE youtube_channels ADD COLUMN affiliate_channel_name VARCHAR(200) DEFAULT ''")
        print("Added affiliate_channel_name to youtube_channels.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column affiliate_channel_name already exists.")
        else:
            print("Error adding column affiliate_channel_name:", e)

    try:
        cursor.execute("ALTER TABLE youtube_channels ADD COLUMN affiliate_link VARCHAR(500) DEFAULT ''")
        print("Added affiliate_link to youtube_channels.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column affiliate_link already exists.")
        else:
            print("Error adding column affiliate_link:", e)

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

    # 5. Create affiliate_channels table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS affiliate_channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        youtube_channel_id INTEGER NOT NULL REFERENCES youtube_channels(id),
        name VARCHAR(200) NOT NULL,
        link VARCHAR(500) DEFAULT '',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print("Checked affiliate_channels table.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    migrate()
