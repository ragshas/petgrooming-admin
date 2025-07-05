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

# Create bills table if it doesn't exist
c.execute('''
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    service TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers (id)
)
''')


conn.commit()
conn.close()

print("Database initialized successfully! Customers and Bills tables are ready.")
