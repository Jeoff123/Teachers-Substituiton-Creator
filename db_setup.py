import sqlite3

def create_database():
    # Connect to SQLite database (it will be created if it does not exist)
    conn = sqlite3.connect('new_timetable.db')
    c = conn.cursor()

    # Drop the timetable table if it exists (for a clean slate)
    c.execute('DROP TABLE IF EXISTS timetable')

    # Create the timetable table
    c.execute('''
    CREATE TABLE timetable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day TEXT NOT NULL,
        teacher TEXT NOT NULL,
        period1 TEXT,
        period2 TEXT,
        period3 TEXT,
        period4 TEXT,
        period5 TEXT,
        period6 TEXT,
        period7 TEXT,
        period8 TEXT
    )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
    print("Database setup complete.")
