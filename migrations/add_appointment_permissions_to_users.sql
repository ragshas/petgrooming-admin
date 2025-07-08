-- Migration: Add appointment edit/delete permissions to users table
ALTER TABLE users ADD COLUMN can_edit_appointment INTEGER NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN can_delete_appointment INTEGER NOT NULL DEFAULT 0;
