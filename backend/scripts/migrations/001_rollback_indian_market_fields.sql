-- Rollback Migration: Remove Indian Market Support Fields
-- Description: Removes fields added for Indian job market support

-- Drop indexes first
DROP INDEX IF EXISTS idx_indian_salary_industry;
DROP INDEX IF EXISTS idx_indian_salary_company_type;
DROP INDEX IF EXISTS idx_indian_salary_location;
DROP INDEX IF EXISTS idx_indian_salary_experience;
DROP INDEX IF EXISTS idx_indian_salary_job_title;

DROP INDEX IF EXISTS idx_jobs_salary_currency;
DROP INDEX IF EXISTS idx_jobs_country;
DROP INDEX IF EXISTS idx_jobs_company_type;
DROP INDEX IF EXISTS idx_jobs_city_tier;

-- Drop indian_salary_data table
DROP TABLE IF EXISTS indian_salary_data;

-- Remove fields from companies table
ALTER TABLE companies DROP COLUMN IF EXISTS headquarters_country;
ALTER TABLE companies DROP COLUMN IF EXISTS company_type;

-- Remove fields from jobs table
ALTER TABLE jobs DROP COLUMN IF EXISTS company_type;
ALTER TABLE jobs DROP COLUMN IF EXISTS salary_currency;
ALTER TABLE jobs DROP COLUMN IF EXISTS city_tier;
ALTER TABLE jobs DROP COLUMN IF EXISTS country;

-- Remove field from user_profiles table
ALTER TABLE user_profiles DROP COLUMN IF EXISTS education_institution;

-- Remove field from users table
ALTER TABLE users DROP COLUMN IF EXISTS country;
