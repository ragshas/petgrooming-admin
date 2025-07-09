#manual This is a script to initialize a SQLite database for a pet grooming management system.
# It creates tables for customers, bills, users, and appointments, and inserts some initial data

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
    can_edit_customer INTEGER DEFAULT 0,
    can_delete_customer INTEGER DEFAULT 0,
    can_add_bill INTEGER DEFAULT 1,
    can_edit_bill INTEGER DEFAULT 0,
    can_delete_bill INTEGER DEFAULT 0
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    pet_name TEXT,
    service TEXT NOT NULL,
    date TEXT NOT NULL,  -- format: YYYY-MM-DD
    time TEXT NOT NULL,  -- format: HH:MM
    notes TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
''')

c.execute('''INSERT INTO appointments (customer_id, pet_name, service, date, time, notes)
VALUES
 (1, 'Buddy', 'Haircut', '2025-07-07', '10:00', 'Regular trim'),
 (2, 'Luna', 'Bath', '2025-07-08', '14:00', ''),
 (3, 'Max', 'Nail Clipping', '2025-07-09', '16:00', 'First visit');
''')

conn.commit()
conn.close()

print("Database initialized successfully! Customers, Bills, and Users tables are ready.")
