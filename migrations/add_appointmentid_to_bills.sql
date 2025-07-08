-- Migration: Add appointment_id to bills table
ALTER TABLE bills ADD COLUMN appointment_id INTEGER;
-- Optionally, you can backfill this column with data if you have a way to match existing bills to appointments.
-- You may also want to add a FOREIGN KEY constraint if your SQLite version supports it:
-- ALTER TABLE bills ADD CONSTRAINT fk_appointment FOREIGN KEY (appointment_id) REFERENCES appointments(id);
