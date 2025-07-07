-- Migration: Add date_added column to customers table
ALTER TABLE customers ADD COLUMN date_added TEXT DEFAULT NULL;
