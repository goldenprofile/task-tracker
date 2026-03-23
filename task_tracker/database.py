"""Database initialization and session management."""

from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base


def get_database_path() -> Path:
    """Get the path to the database file."""
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir / "tasks.db"


def get_engine():
    """Create and return the database engine."""
    db_path = get_database_path()
    return create_engine(f"sqlite:///{db_path}", echo=False)


def init_database() -> None:
    """Initialize the database and create tables."""
    engine = get_engine()
    Base.metadata.create_all(engine)


def get_session() -> Session:
    """Get a new database session."""
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def get_session_context() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class DatabaseManager:
    """Database manager for the application."""

    def __init__(self):
        self._engine = None
        self._session_factory = None

    def initialize(self) -> None:
        """Initialize the database."""
        self._engine = get_engine()
        Base.metadata.create_all(self._engine)
        self._session_factory = sessionmaker(bind=self._engine)

    def get_session(self) -> Session:
        """Get a new session."""
        if self._session_factory is None:
            self.initialize()
        return self._session_factory()

    def close(self) -> None:
        """Close the database connection."""
        if self._engine:
            self._engine.dispose()


# Global database manager instance
db_manager = DatabaseManager()
