-- Migration: Move pet data to pets table and link appointments

-- 1. Insert pets for each customer (if not already present)
INSERT INTO pets (customer_id, pet_name, pet_type, notes)
SELECT id, pet_name, pet_type, notes FROM customers WHERE pet_name IS NOT NULL AND pet_name != '';

-- 2. For each appointment, set pet_id to the matching pet (by customer and pet_name)
UPDATE appointments
SET pet_id = (
    SELECT pets.id FROM pets
    WHERE pets.customer_id = appointments.customer_id
      AND pets.pet_name = appointments.pet_name
    LIMIT 1
)
WHERE pet_id IS NULL;

-- 3. (Optional) Remove pet_name and pet_type columns from appointments after code update
-- SQLite does not support DROP COLUMN directly; you would need to recreate the table if you want to fully remove them.
