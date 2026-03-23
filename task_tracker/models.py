"""SQLAlchemy models for Task Tracker."""

from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import String, Text, ForeignKey, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class TaskStatus(str, Enum):
    """Task status enumeration."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Project(Base):
    """Project model."""
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(20), default="blue")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)

    tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="project", cascade="all, delete-orphan"
    )

    @property
    def task_count(self) -> int:
        """Get total number of tasks."""
        return len(self.tasks)

    @property
    def completed_count(self) -> int:
        """Get number of completed tasks."""
        return len([t for t in self.tasks if t.status == TaskStatus.DONE])

    @property
    def completion_percentage(self) -> int:
        """Get completion percentage."""
        if self.task_count == 0:
            return 0
        return int((self.completed_count / self.task_count) * 100)

    def __repr__(self) -> str:
        return f"Project(id={self.id}, name='{self.name}')"


class Task(Base):
    """Task model."""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus), default=TaskStatus.TODO
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SQLEnum(TaskPriority), default=TaskPriority.MEDIUM
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date and self.status != TaskStatus.DONE:
            return datetime.now() > self.due_date
        return False

    @property
    def priority_symbol(self) -> str:
        """Get priority symbol for display."""
        symbols = {
            TaskPriority.LOW: "↓",
            TaskPriority.MEDIUM: "→",
            TaskPriority.HIGH: "↑",
        }
        return symbols.get(self.priority, "→")

    @property
    def status_symbol(self) -> str:
        """Get status symbol for display."""
        symbols = {
            TaskStatus.TODO: "☐",
            TaskStatus.IN_PROGRESS: "◐",
            TaskStatus.DONE: "☑",
        }
        return symbols.get(self.status, "☐")

    def __repr__(self) -> str:
        return f"Task(id={self.id}, title='{self.title}', status={self.status.value})"
