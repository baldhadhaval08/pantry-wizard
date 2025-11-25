"""Database configuration and session management."""
from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False  # Set to True for SQL query logging
)


def init_db():
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency for getting database session."""
    with Session(engine) as session:
        yield session

