import sqlite3

DB_PATH = "database.db"  # Update path if needed

tables = [
    "bills",
    "appointments",
    "pets",
    "customers",
    # Add any other tables you want to clear
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for table in tables:
    c.execute(f"DELETE FROM {table};")
    # Optionally reset auto-increment (uncomment if needed)
    # c.execute(f'DELETE FROM sqlite_sequence WHERE name="{table}";')

conn.commit()
conn.close()
print("All specified tables have been cleared.")