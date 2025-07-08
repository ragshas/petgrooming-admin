-- Migration: Add UNIQUE constraint to phone in customers table
PRAGMA foreign_keys=off;

BEGIN TRANSACTION;

CREATE TABLE customers_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    email TEXT,
    pet_name TEXT,
    pet_type TEXT,
    notes TEXT,
    date_added TEXT
);

INSERT INTO customers_new (id, name, phone, email, pet_name, pet_type, notes, date_added)
SELECT id, name, phone, email, pet_name, pet_type, notes, date_added FROM customers;

DROP TABLE customers;
ALTER TABLE customers_new RENAME TO customers;

COMMIT;

PRAGMA foreign_keys=on;
