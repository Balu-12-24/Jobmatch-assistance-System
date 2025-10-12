# Database Migrations

This directory contains SQL migration scripts for the JobMatch AI database.

## Migration Files

### 001_add_indian_market_fields.sql
Adds support for Indian job market including:
- Country field for users
- Education institution tracking for IIT/NIT/IIM
- City tier classification (1, 2, 3)
- Company type (MNC, startup, service, product, BPO, KPO)
- Salary currency (INR, USD, etc.)
- Indian salary data table for training ML models

### 001_rollback_indian_market_fields.sql
Rollback script to remove Indian market fields if needed.

## Running Migrations

### Using Python Script (Recommended)
```bash
cd backend
python scripts/run_migration.py
```

### Using psql (Manual)
```bash
psql $DATABASE_URL -f scripts/migrations/001_add_indian_market_fields.sql
```

## Rollback

To rollback the migration:
```bash
psql $DATABASE_URL -f scripts/migrations/001_rollback_indian_market_fields.sql
```

## Creating New Migrations

1. Create a new SQL file with naming convention: `XXX_description.sql`
2. Create corresponding rollback file: `XXX_rollback_description.sql`
3. Run using the migration script

## Notes

- Migrations are run in alphabetical order
- Always test migrations on a development database first
- Keep rollback scripts up to date
- Document all schema changes in migration files
