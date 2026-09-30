import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.config import settings

# Configure engine with connect_args for SQLite if needed
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency that provides a database session and ensures closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Checks if the database is accessible."""
    try:
        with engine.connect() as conn:
            return True
    except Exception:
        return False
