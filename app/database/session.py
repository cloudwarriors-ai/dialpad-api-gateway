from sqlalchemy.orm import Session
from app.database.connection import SessionLocal


def get_db():
    """
    Dependency function to get a database session.
    
    Yields:
        Session: A SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_context():
    """
    Context manager for database sessions.
    
    Usage:
    ```
    with get_db_context() as db:
        db.query(Model).all()
    ```
    
    Returns:
        Session: A SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()