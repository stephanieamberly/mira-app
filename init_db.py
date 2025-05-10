import sqlite3

DB_FILE = "mira_resumes.db"

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# Create all required tables
cur.execute("""
CREATE TABLE IF NOT EXISTS mira_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    answer TEXT,
    timestamp TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS onboarding_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    position TEXT,
    start_date TEXT,
    salary REAL,
    filepath TEXT,
    timestamp TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS job_descriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    timestamp TEXT
)
""")

conn.commit()
conn.close()
print("Database tables created.")
