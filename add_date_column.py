import sqlite3

db_file = 'database.db'

conn = sqlite3.connect(db_file)
c = conn.cursor()

try:
    # Add column with NULL initially
    c.execute("ALTER TABLE customers ADD COLUMN date_added TEXT")
    print("✅ Column 'date_added' added.")
except sqlite3.OperationalError as e:
    print(f"⚠️ Skipped adding column: {e}")

# Step 2: set date_added for existing rows
c.execute("UPDATE customers SET date_added = datetime('now') WHERE date_added IS NULL")
conn.commit()
print("✅ Existing rows updated with current datetime.")

conn.close()
