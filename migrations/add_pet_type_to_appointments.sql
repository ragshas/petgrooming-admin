-- Migration: Add pet_type column to appointments table
ALTER TABLE appointments ADD COLUMN pet_type TEXT;
