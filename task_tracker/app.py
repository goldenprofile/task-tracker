"""NiceGUI application for Task Tracker."""

from nicegui import ui, app

from .theme import Colors, inject_theme_css
from .state import app_state
from .database import db_manager
from .models import Project, Task, TaskStatus, TaskPriority
from .components.sidebar import build_sidebar
from .components.kanban import build_kanban_board
from .components.dialogs import (
    show_project_dialog,
    show_task_dialog,
    show_confirm_dialog,
    show_search_dialog,
    show_filter_dialog,
    show_help_dialog,
)


@ui.page("/")
def main_page():
    """Main application page."""
    ui.dark_mode(True)
    inject_theme_css()

    # Initialize database
    db_manager.initialize()
    app_state.load_projects()
    if app_state.projects and not app_state.current_project:
        app_state.select_project(app_state.projects[0])

    # State: references to containers for refreshing
    state = {}

    def refresh_all():
        """Refresh sidebar and kanban board."""
        refresh_sidebar()
        refresh_board()

    def refresh_sidebar():
        if "sidebar_list" in state and hasattr(state["sidebar_list"], "render_projects"):
            state["sidebar_list"].render_projects()

    def refresh_board():
        if "board" in state:
            state["board"].clear()
            with state["board"]:
                _build_board_content(state)

    def _build_board_content(state):
        """Build board content — extracted for refresh."""
        board = build_kanban_board(
            on_task_edit=lambda t: _show_edit_task_dialog(t, refresh_all),
            on_task_delete=lambda t: _show_delete_task_dialog(t, refresh_all),
            on_add_task=lambda: _show_new_task_dialog(refresh_all),
            on_filter=lambda: show_filter_dialog(on_apply=refresh_all),
            on_search=lambda: show_search_dialog(on_search=lambda q: refresh_all()),
        )

    # Set up update callback
    app_state.set_update_callback(refresh_all)

    # Handle drag-and-drop events
    ui.on("task_moved", lambda e: _handle_task_moved(e, refresh_all))

    # Layout: sidebar + board
    with ui.row().classes("w-full h-screen no-wrap m-0 p-0"):
        state["sidebar_list"] = build_sidebar(
            on_new_project=lambda: _show_new_project_dialog(refresh_all),
            on_edit_project=lambda p: _show_edit_project_dialog(p, refresh_all),
            on_delete_project=lambda p: _show_delete_project_dialog(p, refresh_all),
            on_help=show_help_dialog,
            refresh_board=refresh_all,
        )

        # Board wrapper
        board_wrapper = ui.column().classes("flex-1 h-screen overflow-hidden")
        state["board"] = board_wrapper
        with board_wrapper:
            _build_board_content(state)

    # Keyboard shortcuts
    _setup_keyboard_shortcuts(state, refresh_all)


def _handle_task_moved(e, refresh_all):
    """Handle drag-and-drop task move."""
    data = e.args
    task_id = data.get("task_id")
    new_status = data.get("new_status")
    if task_id and new_status:
        try:
            status = TaskStatus(new_status)
            app_state.move_task(task_id, status)
        except (ValueError, Exception):
            pass


def _setup_keyboard_shortcuts(state, refresh_all):
    """Set up keyboard event handlers."""
    def handle_key(e):
        # Ignore if typing in input
        if e.args.get("targetTagName", "").lower() in ("input", "textarea"):
            return

        key = e.args.get("key", "")
        ctrl = e.args.get("ctrlKey", False)
        shift = e.args.get("shiftKey", False)

        if ctrl and key.lower() == "n":
            if shift:
                _show_new_project_dialog(refresh_all)
            elif app_state.current_project:
                _show_new_task_dialog(refresh_all)
        elif ctrl and key.lower() == "e":
            if app_state.current_task:
                _show_edit_task_dialog(app_state.current_task, refresh_all)
            elif app_state.current_project:
                _show_edit_project_dialog(app_state.current_project, refresh_all)
        elif ctrl and key.lower() == "f":
            show_search_dialog(on_search=lambda q: refresh_all())
        elif key == "Delete":
            if app_state.current_task:
                _show_delete_task_dialog(app_state.current_task, refresh_all)
        elif key == "f" and not ctrl:
            show_filter_dialog(on_apply=refresh_all)
        elif key == "a" and not ctrl:
            app_state.show_archived = not app_state.show_archived
            app_state.load_projects()
            app_state.notify_update()
        elif key == "?":
            show_help_dialog()
        elif key == "Tab":
            _switch_project(not shift)
            refresh_all()

    ui.on("keydown", handle_key)
    ui.run_javascript("""
        document.addEventListener('keydown', (e) => {
            // Prevent default for Tab to avoid focus change
            if (e.key === 'Tab') e.preventDefault();
            // Prevent default for Ctrl+N, Ctrl+F to avoid browser actions
            if (e.ctrlKey && (e.key === 'n' || e.key === 'N' || e.key === 'f')) e.preventDefault();

            emitEvent('keydown', {
                key: e.key,
                ctrlKey: e.ctrlKey,
                shiftKey: e.shiftKey,
                altKey: e.altKey,
                targetTagName: e.target.tagName,
            });
        });
    """)


def _switch_project(forward: bool = True):
    """Switch to next/previous project."""
    if not app_state.projects:
        return
    current_idx = 0
    if app_state.current_project:
        for i, p in enumerate(app_state.projects):
            if p.id == app_state.current_project.id:
                current_idx = i
                break
    if forward:
        next_idx = (current_idx + 1) % len(app_state.projects)
    else:
        next_idx = (current_idx - 1) % len(app_state.projects)
    app_state.select_project(app_state.projects[next_idx])


# === Dialog Wrappers ===

def _show_new_project_dialog(refresh_all):
    def on_save(name, description, color, archived):
        app_state.create_project(name, description, color)

    show_project_dialog(on_save=on_save)


def _show_edit_project_dialog(project: Project, refresh_all):
    def on_save(name, description, color, archived):
        app_state.update_project(
            project.id, name=name, description=description,
            color=color, archived=archived,
        )

    show_project_dialog(on_save=on_save, project=project)


def _show_delete_project_dialog(project: Project, refresh_all):
    def on_confirm():
        app_state.delete_project(project.id)

    show_confirm_dialog(
        title="Delete Project",
        message=f'Are you sure you want to delete "{project.name}"?\nAll tasks will be permanently deleted.',
        on_confirm=on_confirm,
    )


def _show_new_task_dialog(refresh_all):
    if not app_state.current_project:
        return

    def on_save(title, description, status, priority, due_date):
        app_state.create_task(
            project_id=app_state.current_project.id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
        )
        if status != TaskStatus.TODO:
            app_state.load_projects()
            for task in app_state.current_project.tasks:
                if task.title == title:
                    app_state.update_task(task.id, status=status)
                    break

    show_task_dialog(on_save=on_save)


def _show_edit_task_dialog(task: Task, refresh_all):
    def on_save(title, description, status, priority, due_date):
        app_state.update_task(
            task.id, title=title, description=description,
            status=status, priority=priority, due_date=due_date,
        )

    show_task_dialog(on_save=on_save, task=task)


def _show_delete_task_dialog(task: Task, refresh_all):
    def on_confirm():
        app_state.delete_task(task.id)

    show_confirm_dialog(
        title="Delete Task",
        message=f'Are you sure you want to delete "{task.title}"?',
        on_confirm=on_confirm,
    )
