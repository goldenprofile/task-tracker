"""Database initialization and session management."""

import sqlite3
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
        self._migrate_database()
        Base.metadata.create_all(self._engine)
        self._session_factory = sessionmaker(bind=self._engine)

    def _migrate_database(self) -> None:
        """Apply schema migrations for existing databases."""
        db_path = get_database_path()
        if not db_path.exists():
            return

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        try:
            cursor.execute("PRAGMA table_info(tasks)")
            columns = {row[1]: row for row in cursor.fetchall()}

            if not columns:
                return  # Table doesn't exist yet

            needs_rebuild = False
            # Check if project_id has NOT NULL constraint (notnull=1)
            if "project_id" in columns and columns["project_id"][3] == 1:
                needs_rebuild = True

            has_start_date = "start_date" in columns

            if needs_rebuild:
                existing_cols = "id, project_id, title, description, status, priority, due_date, created_at, completed_at"
                start_date_select = ", start_date" if has_start_date else ", NULL AS start_date"

                cursor.execute("PRAGMA foreign_keys=OFF")
                cursor.execute("BEGIN TRANSACTION")
                cursor.execute("""
                    CREATE TABLE tasks_new (
                        id INTEGER PRIMARY KEY,
                        project_id INTEGER REFERENCES projects(id),
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        status VARCHAR(11),
                        priority VARCHAR(6),
                        start_date DATETIME,
                        due_date DATETIME,
                        created_at DATETIME,
                        completed_at DATETIME
                    )
                """)
                cursor.execute(f"""
                    INSERT INTO tasks_new (
                        {existing_cols}, start_date
                    ) SELECT {existing_cols}{start_date_select} FROM tasks
                """)
                cursor.execute("DROP TABLE tasks")
                cursor.execute("ALTER TABLE tasks_new RENAME TO tasks")
                cursor.execute("COMMIT")
                cursor.execute("PRAGMA foreign_keys=ON")
            elif not has_start_date:
                cursor.execute("ALTER TABLE tasks ADD COLUMN start_date DATETIME")

            conn.commit()
        finally:
            conn.close()

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
