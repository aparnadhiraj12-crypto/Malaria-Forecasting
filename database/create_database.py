import sqlite3
import os

# =====================================================
# DATABASE LOCATION
# =====================================================

db_path = r"C:\Users\M. Srinivasa Rao\Shraddha Code\Forecasting\database\malaria.db"

# Create database folder if it doesn't exist
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Connect to database
conn = sqlite3.connect(db_path)

cursor = conn.cursor()

# =====================================================
# CREATE MALARIA TABLE
# =====================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS malaria_cases (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    state TEXT NOT NULL,

    month TEXT NOT NULL,

    cases INTEGER NOT NULL,

    log_cases REAL NOT NULL,

    UNIQUE(state, month)

)

""")

conn.commit()

conn.close()

print("=" * 50)
print("Malaria Database Created Successfully!")
print("Database Location:")
print(db_path)
print("=" * 50)