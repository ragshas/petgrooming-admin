import sqlite3
import pytest
import os

# Import the migration logic from add_date_column.py as a function for testability
from add_date_column import main as run_migration

def setup_customers_table(conn):
    c = conn.cursor()
    c.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    """)
    c.executemany("INSERT INTO customers (name) VALUES (?)", [("Alice",), ("Bob",)])
    conn.commit()

@pytest.fixture
def in_memory_db(monkeypatch):
    # Patch sqlite3.connect to use in-memory DB
    conn = sqlite3.connect(":memory:")
    setup_customers_table(conn)
    monkeypatch.setattr("add_date_column.db_file", ":memory:")
    monkeypatch.setattr("add_date_column.conn", conn)
    yield conn
    conn.close()

def test_add_date_column_and_update(in_memory_db, monkeypatch):
    # Run the migration logic
    run_migration()
    c = in_memory_db.cursor()
    # Check if column exists
    c.execute("PRAGMA table_info(customers)")
    columns = [row[1] for row in c.fetchall()]
    assert "date_added" in columns
    # Check if all rows have date_added set
    c.execute("SELECT date_added FROM customers")
    results = c.fetchall()
    assert all(row[0] is not None for row in results)
