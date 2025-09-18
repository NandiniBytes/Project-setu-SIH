"""
Production Database Configuration for Project Setu
Supports PostgreSQL, MySQL, and SQLite with connection pooling and monitoring
"""

import os
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool
import time

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./project_setu_prod.db")

# Production database configurations
PRODUCTION_DB_CONFIG = {
    "postgresql": {
        "pool_size": 20,
        "max_overflow": 30,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "echo": False,
        "connect_args": {
            "sslmode": "require",
            "application_name": "project_setu_healthcare"
        }
    },
    "mysql": {
        "pool_size": 20,
        "max_overflow": 30,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "echo": False,
        "connect_args": {
            "charset": "utf8mb4",
            "autocommit": True
        }
    },
    "sqlite": {
        "poolclass": StaticPool,
        "connect_args": {
            "check_same_thread": False,
            "timeout": 30
        },
        "echo": False
    }
}

def get_db_type(database_url: str) -> str:
    """Determine database type from URL"""
    if database_url.startswith("postgresql://") or database_url.startswith("postgres://"):
        return "postgresql"
    elif database_url.startswith("mysql://"):
        return "mysql"
    else:
        return "sqlite"

def create_production_engine():
    """Create production database engine with appropriate configuration"""
    db_type = get_db_type(DATABASE_URL)
    config = PRODUCTION_DB_CONFIG[db_type]
    
    logger.info(f"Creating {db_type} database engine for production")
    
    # Create engine with production settings
    engine = create_engine(DATABASE_URL, **config)
    
    # Add connection event listeners for monitoring
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if db_type == "sqlite":
            # Enable WAL mode and other optimizations for SQLite
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=1000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.close()
    
    @event.listens_for(engine, "checkout")
    def receive_checkout(dbapi_connection, connection_record, connection_proxy):
        """Log connection checkout for monitoring"""
        connection_record.info['checkout_time'] = time.time()
        logger.debug("Database connection checked out")
    
    @event.listens_for(engine, "checkin")
    def receive_checkin(dbapi_connection, connection_record):
        """Log connection checkin and duration"""
        if 'checkout_time' in connection_record.info:
            duration = time.time() - connection_record.info['checkout_time']
            logger.debug(f"Database connection checked in after {duration:.2f}s")
    
    return engine

# Create production engine
engine = create_production_engine()

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Important for production
)

# Create base class for models
Base = declarative_base()

def get_db():
    """
    Dependency to get database session.
    Includes proper error handling and cleanup for production.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def check_database_health():
    """Check database connectivity and health"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            result.fetchone()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# Database connection monitoring
class DatabaseMetrics:
    """Track database connection metrics for monitoring"""
    
    def __init__(self):
        self.connection_count = 0
        self.query_count = 0
        self.error_count = 0
        self.total_query_time = 0.0
    
    def record_connection(self):
        self.connection_count += 1
    
    def record_query(self, duration: float):
        self.query_count += 1
        self.total_query_time += duration
    
    def record_error(self):
        self.error_count += 1
    
    def get_stats(self):
        avg_query_time = self.total_query_time / max(self.query_count, 1)
        return {
            "connections": self.connection_count,
            "queries": self.query_count,
            "errors": self.error_count,
            "avg_query_time": avg_query_time
        }

# Global metrics instance
db_metrics = DatabaseMetrics()

# Database migration support
def run_migrations():
    """Run database migrations for production deployment"""
    try:
        # This would typically use Alembic for real migrations
        logger.info("Running database migrations...")
        create_tables()
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        raise

# Backup utilities for production
def create_database_backup():
    """Create database backup (implementation depends on DB type)"""
    db_type = get_db_type(DATABASE_URL)
    backup_filename = f"project_setu_backup_{int(time.time())}.sql"
    
    try:
        if db_type == "postgresql":
            # Use pg_dump for PostgreSQL
            os.system(f"pg_dump {DATABASE_URL} > {backup_filename}")
        elif db_type == "mysql":
            # Use mysqldump for MySQL
            os.system(f"mysqldump {DATABASE_URL} > {backup_filename}")
        elif db_type == "sqlite":
            # Use sqlite3 .dump for SQLite
            db_path = DATABASE_URL.replace("sqlite:///", "")
            os.system(f"sqlite3 {db_path} .dump > {backup_filename}")
        
        logger.info(f"Database backup created: {backup_filename}")
        return backup_filename
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        raise
