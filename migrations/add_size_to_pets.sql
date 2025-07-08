ALTER TABLE pets ADD COLUMN size TEXT CHECK(size IN ('small','medium','large')) DEFAULT 'medium';
