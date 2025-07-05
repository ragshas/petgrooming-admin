import sqlite3
from werkzeug.security import generate_password_hash

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

# Create users table with roles and permissions
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    can_add_customer INTEGER DEFAULT 1,
    can_edit_customer INTEGER DEFAULT 1,
    can_delete_customer INTEGER DEFAULT 1,
    can_add_bill INTEGER DEFAULT 1,
    can_edit_bill INTEGER DEFAULT 1,
    can_delete_bill INTEGER DEFAULT 1
)
''')
# Insert default admin if not exists
c.execute('SELECT * FROM users WHERE username=?', ('admin',))
if not c.fetchone():
    admin_pw = generate_password_hash('admin123')
    c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ('admin', admin_pw, 'admin'))

conn.commit()
conn.close()

print("Database initialized successfully! Customers, Bills, and Users tables are ready.")
