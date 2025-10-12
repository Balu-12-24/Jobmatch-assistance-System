-- Migration: Add Indian Market Support Fields
-- Description: Adds fields for Indian job market support including city tiers, company types, and salary data

-- Add country field to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS country VARCHAR(50) DEFAULT 'India';

-- Add education_institution field to user_profiles table
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS education_institution VARCHAR(255);

-- Add Indian market fields to jobs table
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS country VARCHAR(50) DEFAULT 'India';
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS city_tier INTEGER;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS salary_currency VARCHAR(10) DEFAULT 'INR';
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS company_type VARCHAR(50);

-- Add company type fields to companies table
ALTER TABLE companies ADD COLUMN IF NOT EXISTS company_type VARCHAR(50);

-- Add company type fields to companies table
ALTER TABLE companies ADD COLUMN IF NOT EXISTS company_type VARCHAR(50);
ALTER TABLE companies ADD COLUMN IF NOT EXISTS headquarters_country VARCHAR(50);

-- Create indian_salary_data table
CREATE TABLE IF NOT EXISTS indian_salary_data (
    id SERIAL PRIMARY KEY,
    job_title VARCHAR(255),
    experience_years INTEGER,
    location VARCHAR(255),
    city_tier INTEGER,
    company_type VARCHAR(50),
    skills JSONB,
    salary_lpa DECIMAL(10, 2),
    salary_inr_annual INTEGER,
    industry VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_jobs_city_tier ON jobs(city_tier);
CREATE INDEX IF NOT EXISTS idx_jobs_company_type ON jobs(company_type);
CREATE INDEX IF NOT EXISTS idx_jobs_country ON jobs(country);
CREATE INDEX IF NOT EXISTS idx_jobs_salary_currency ON jobs(salary_currency);

CREATE INDEX IF NOT EXISTS idx_indian_salary_job_title ON indian_salary_data(job_title);
CREATE INDEX IF NOT EXISTS idx_indian_salary_experience ON indian_salary_data(experience_years);
CREATE INDEX IF NOT EXISTS idx_indian_salary_location ON indian_salary_data(location);
CREATE INDEX IF NOT EXISTS idx_indian_salary_company_type ON indian_salary_data(company_type);
CREATE INDEX IF NOT EXISTS idx_indian_salary_industry ON indian_salary_data(industry);

-- Add comments for documentation
COMMENT ON COLUMN jobs.city_tier IS 'City tier classification: 1=Tier 1 (Bangalore, Mumbai, etc.), 2=Tier 2, 3=Tier 3';
COMMENT ON COLUMN jobs.company_type IS 'Company type: MNC, startup, service, product, BPO, KPO';
COMMENT ON COLUMN jobs.salary_currency IS 'Salary currency: INR, USD, etc.';
COMMENT ON COLUMN indian_salary_data.salary_lpa IS 'Salary in Lakhs Per Annum (LPA)';
COMMENT ON COLUMN indian_salary_data.salary_inr_annual IS 'Annual salary in Indian Rupees';
