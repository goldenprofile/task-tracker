"""Application state management for Task Tracker."""

from typing import Optional, List, Callable
from dataclasses import dataclass, field

from sqlalchemy.orm import selectinload

from .models import Project, Task, TaskStatus, TaskPriority
from .database import db_manager


@dataclass
class AppState:
    """Global application state."""

    # Data
    projects: List[Project] = field(default_factory=list)
    current_project: Optional[Project] = None
    current_task: Optional[Task] = None

    # Filters
    show_archived: bool = False
    filter_status: Optional[TaskStatus] = None
    filter_priority: Optional[TaskPriority] = None
    search_query: str = ""

    # UI callbacks
    _on_update: Optional[Callable] = None

    def set_update_callback(self, callback: Callable) -> None:
        """Set callback to be called when state changes."""
        self._on_update = callback

    def notify_update(self) -> None:
        """Notify listeners of state change."""
        if self._on_update:
            self._on_update()

    def load_projects(self) -> None:
        """Load projects from database."""
        session = db_manager.get_session()
        try:
            query = session.query(Project).options(selectinload(Project.tasks))
            if not self.show_archived:
                query = query.filter(Project.archived == False)
            self.projects = query.order_by(Project.created_at.desc()).all()

            # Update current project reference if it exists
            if self.current_project:
                for p in self.projects:
                    if p.id == self.current_project.id:
                        self.current_project = p
                        break
                else:
                    # Current project no longer in list
                    self.current_project = self.projects[0] if self.projects else None
        finally:
            session.close()

    def get_filtered_tasks(self) -> List[Task]:
        """Get tasks filtered by current filters."""
        if not self.current_project:
            return []

        tasks = list(self.current_project.tasks)

        # Apply status filter
        if self.filter_status:
            tasks = [t for t in tasks if t.status == self.filter_status]

        # Apply priority filter
        if self.filter_priority:
            tasks = [t for t in tasks if t.priority == self.filter_priority]

        # Apply search filter
        if self.search_query:
            query = self.search_query.lower()
            tasks = [t for t in tasks if
                     query in t.title.lower() or
                     (t.description and query in t.description.lower())]

        return tasks

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get filtered tasks for a specific status column."""
        tasks = self.get_filtered_tasks()
        return [t for t in tasks if t.status == status]

    def select_project(self, project: Optional[Project]) -> None:
        """Select a project."""
        self.current_project = project
        self.current_task = None
        self.notify_update()

    def select_task(self, task: Optional[Task]) -> None:
        """Select a task."""
        self.current_task = task

    def clear_filters(self) -> None:
        """Clear all filters."""
        self.filter_status = None
        self.filter_priority = None
        self.search_query = ""
        self.notify_update()

    def create_project(self, name: str, description: str = "", color: str = "blue") -> Project:
        """Create a new project."""
        session = db_manager.get_session()
        try:
            project = Project(name=name, description=description, color=color)
            session.add(project)
            session.commit()
            session.refresh(project)
            self.load_projects()
            self.select_project(project)
            return project
        finally:
            session.close()

    def update_project(self, project_id: int, **kwargs) -> None:
        """Update a project."""
        session = db_manager.get_session()
        try:
            project = session.query(Project).get(project_id)
            if project:
                for key, value in kwargs.items():
                    setattr(project, key, value)
                session.commit()
            self.load_projects()
            self.notify_update()
        finally:
            session.close()

    def delete_project(self, project_id: int) -> None:
        """Delete a project."""
        session = db_manager.get_session()
        try:
            project = session.query(Project).get(project_id)
            if project:
                session.delete(project)
                session.commit()

            if self.current_project and self.current_project.id == project_id:
                self.current_project = None

            self.load_projects()
            if not self.current_project and self.projects:
                self.select_project(self.projects[0])
            self.notify_update()
        finally:
            session.close()

    def create_task(self, project_id: int, title: str, description: str = "",
                    priority: TaskPriority = TaskPriority.MEDIUM,
                    due_date=None) -> Task:
        """Create a new task."""
        session = db_manager.get_session()
        try:
            task = Task(
                project_id=project_id,
                title=title,
                description=description,
                priority=priority,
                due_date=due_date
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            self.load_projects()
            self.notify_update()
            return task
        finally:
            session.close()

    def update_task(self, task_id: int, **kwargs) -> None:
        """Update a task."""
        session = db_manager.get_session()
        try:
            task = session.query(Task).get(task_id)
            if task:
                # Handle status change to DONE
                if 'status' in kwargs and kwargs['status'] == TaskStatus.DONE:
                    from datetime import datetime
                    kwargs['completed_at'] = datetime.now()
                elif 'status' in kwargs and kwargs['status'] != TaskStatus.DONE:
                    kwargs['completed_at'] = None

                for key, value in kwargs.items():
                    setattr(task, key, value)
                session.commit()
            self.load_projects()
            self.notify_update()
        finally:
            session.close()

    def delete_task(self, task_id: int) -> None:
        """Delete a task."""
        session = db_manager.get_session()
        try:
            task = session.query(Task).get(task_id)
            if task:
                session.delete(task)
                session.commit()

            if self.current_task and self.current_task.id == task_id:
                self.current_task = None

            self.load_projects()
            self.notify_update()
        finally:
            session.close()

    def move_task(self, task_id: int, new_status: TaskStatus) -> None:
        """Move a task to a new status (for drag-and-drop)."""
        self.update_task(task_id, status=new_status)


# Global state instance
app_state = AppState()
