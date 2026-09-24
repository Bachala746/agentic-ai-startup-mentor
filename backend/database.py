import sqlite3

DATABASE = "startup_mentor.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS startup_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            startup_idea TEXT NOT NULL,
            mentor TEXT,
            market_analysis TEXT,
            financial_analysis TEXT,
            risk_analysis TEXT,
            roadmap TEXT,
            roadmap_progress TEXT DEFAULT '[]',
            final_decision TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    try:
        cursor.execute(
            "ALTER TABLE startup_plans ADD COLUMN roadmap_progress TEXT DEFAULT '[]'"
        )
    except sqlite3.OperationalError:
        pass

    connection.commit()
    connection.close()