-- Fix missing country column in jobs table
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS country VARCHAR(50) DEFAULT 'India';
