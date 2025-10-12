"""
Database migration runner script.
Runs SQL migration files in order.
"""
import sys
from pathlib import Path
import logging

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from app.core.database import engine
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration(migration_file: Path):
    """Run a single migration file"""
    logger.info(f"Running migration: {migration_file.name}")
    
    try:
        with open(migration_file, 'r') as f:
            sql_content = f.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        with engine.connect() as conn:
            for statement in statements:
                if statement and not statement.startswith('--'):
                    try:
                        conn.execute(text(statement))
                    except Exception as e:
                        logger.warning(f"Statement warning (may be expected): {e}")
            
            conn.commit()
        
        logger.info(f"Migration {migration_file.name} completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Migration {migration_file.name} failed: {e}")
        return False


def run_all_migrations():
    """Run all migration files in order"""
    migrations_dir = Path(__file__).parent / 'migrations'
    
    if not migrations_dir.exists():
        logger.error(f"Migrations directory not found: {migrations_dir}")
        return False
    
    # Get all .sql files sorted by name (exclude rollback files)
    migration_files = sorted([f for f in migrations_dir.glob('*.sql') if 'rollback' not in f.name.lower()])
    
    if not migration_files:
        logger.info("No migration files found")
        return True
    
    logger.info(f"Found {len(migration_files)} migration(s)")
    
    success = True
    for migration_file in migration_files:
        if not run_migration(migration_file):
            success = False
            break
    
    return success


def main():
    """Main migration function"""
    try:
        logger.info("Starting database migrations...")
        
        if run_all_migrations():
            logger.info("All migrations completed successfully!")
        else:
            logger.error("Migration failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Migration process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
