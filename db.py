#used to connect to the SQLite database
# and return a connection object with row factory set to sqlite3.Row
import sqlite3

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
