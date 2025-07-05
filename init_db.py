import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Create customers table
c.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    pet_name TEXT,
    pet_type TEXT,
    notes TEXT
)
''')

conn.commit()
conn.close()

print("✅ Database and table created successfully!")
