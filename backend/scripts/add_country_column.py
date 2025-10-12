"""Add all missing columns directly"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from sqlalchemy import text
from app.core.database import engine

print("Adding missing columns to tables...")

columns = [
    # Jobs table
    "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS country VARCHAR(50) DEFAULT 'India'",
    "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS city_tier INTEGER",
    "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS salary_currency VARCHAR(10) DEFAULT 'INR'",
    "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS company_type VARCHAR(50)",
    # Users table
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS country VARCHAR(50) DEFAULT 'India'",
    # User profiles table
    "ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS education_institution VARCHAR(255)",
    # Companies table
    "ALTER TABLE companies ADD COLUMN IF NOT EXISTS company_type VARCHAR(50)",
    "ALTER TABLE companies ADD COLUMN IF NOT EXISTS headquarters_country VARCHAR(50)"
]

try:
    with engine.connect() as conn:
        for sql in columns:
            print(f"  Executing: {sql[:70]}...")
            conn.execute(text(sql))
        conn.commit()
    print("✅ All columns added successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
