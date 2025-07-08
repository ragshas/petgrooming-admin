-- Migration: Add pets table and link appointments to pets

CREATE TABLE pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    pet_name TEXT NOT NULL,
    pet_type TEXT,
    notes TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

ALTER TABLE appointments ADD COLUMN pet_id INTEGER;
-- (You will need to migrate data and update code to use pet_id)
