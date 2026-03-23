"""NiceGUI dialogs for Task Tracker."""

from datetime import datetime
from typing import Optional, Callable

from nicegui import ui

from ..models import Task, TaskStatus, TaskPriority
from ..theme import Colors
from ..state import app_state


STATUS_OPTIONS = {"To Do": TaskStatus.TODO, "In Progress": TaskStatus.IN_PROGRESS, "Done": TaskStatus.DONE}
PRIORITY_OPTIONS = {"Low": TaskPriority.LOW, "Medium": TaskPriority.MEDIUM, "High": TaskPriority.HIGH}
STATUS_DISPLAY = {v: k for k, v in STATUS_OPTIONS.items()}
PRIORITY_DISPLAY = {v: k for k, v in PRIORITY_OPTIONS.items()}

COLOR_OPTIONS = ["blue", "green", "red", "yellow", "purple", "cyan", "orange", "pink"]


def show_task_dialog(
    on_save: Callable,
    task: Optional[Task] = None,
):
    """Show dialog for creating or editing a task."""
    is_edit = task is not None

    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Edit Task" if is_edit else "New Task").classes(
            "text-lg font-bold"
        ).style(f"color: {Colors.TEXT_PRIMARY}")

        title = ui.input(
            "Title", value=task.title if task else "",
        ).classes("w-full").props('dark')

        desc = ui.textarea(
            "Description", value=(task.description or "") if task else "",
        ).classes("w-full").props('dark')

        with ui.row().classes("w-full gap-4"):
            status = ui.select(
                list(STATUS_OPTIONS.keys()),
                value=STATUS_DISPLAY.get(task.status, "To Do") if task else "To Do",
                label="Status",
            ).classes("flex-1").props('dark')

            priority = ui.select(
                list(PRIORITY_OPTIONS.keys()),
                value=PRIORITY_DISPLAY.get(task.priority, "Medium") if task else "Medium",
                label="Priority",
            ).classes("flex-1").props('dark')

        with ui.row().classes("w-full gap-4"):
            start = ui.input(
                "Start Date (YYYY-MM-DD)",
                value=task.start_date.strftime("%Y-%m-%d") if task and task.start_date else "",
            ).classes("flex-1").props('dark')

            due = ui.input(
                "Due Date (YYYY-MM-DD)",
                value=task.due_date.strftime("%Y-%m-%d") if task and task.due_date else "",
            ).classes("flex-1").props('dark')

        error_label = ui.label("").style(f"color: {Colors.DANGER}; font-size: 12px")

        with ui.row().classes("w-full justify-end gap-2 mt-2"):
            ui.button("Cancel", on_click=dialog.close).props(
                "flat"
            ).style(f"color: {Colors.TEXT_MUTED}")

            def handle_save():
                t = title.value.strip()
                if not t:
                    error_label.set_text("Title is required")
                    return

                d = desc.value.strip()
                s = STATUS_OPTIONS.get(status.value, TaskStatus.TODO)
                p = PRIORITY_OPTIONS.get(priority.value, TaskPriority.MEDIUM)

                start_date = None
                start_str = start.value.strip()
                if start_str:
                    try:
                        start_date = datetime.strptime(start_str, "%Y-%m-%d")
                    except ValueError:
                        error_label.set_text("Invalid start date format. Use YYYY-MM-DD")
                        return

                due_date = None
                date_str = due.value.strip()
                if date_str:
                    try:
                        due_date = datetime.strptime(date_str, "%Y-%m-%d")
                    except ValueError:
                        error_label.set_text("Invalid due date format. Use YYYY-MM-DD")
                        return

                on_save(t, d, s, p, start_date, due_date)
                dialog.close()

            ui.button("Save", on_click=handle_save).style(
                f"background-color: {Colors.ACCENT}; color: white"
            )

    dialog.open()


def show_project_dialog(
    on_save: Callable,
    project=None,
):
    """Show dialog for creating or editing a project."""
    is_edit = project is not None

    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Edit Project" if is_edit else "New Project").classes(
            "text-lg font-bold"
        ).style(f"color: {Colors.TEXT_PRIMARY}")

        name = ui.input(
            "Project Name", value=project.name if project else "",
        ).classes("w-full").props('dark')

        desc = ui.textarea(
            "Description",
            value=(project.description or "") if project else "",
        ).classes("w-full").props('dark')

        color = ui.select(
            COLOR_OPTIONS,
            value=project.color if project else "blue",
            label="Color",
        ).classes("w-full").props('dark')

        archived_val = {"v": project.archived if project else False}
        if is_edit:
            ui.checkbox(
                "Archived", value=archived_val["v"],
                on_change=lambda e: archived_val.update(v=e.value),
            ).style(f"color: {Colors.TEXT_SECONDARY}")

        error_label = ui.label("").style(f"color: {Colors.DANGER}; font-size: 12px")

        with ui.row().classes("w-full justify-end gap-2 mt-2"):
            ui.button("Cancel", on_click=dialog.close).props(
                "flat"
            ).style(f"color: {Colors.TEXT_MUTED}")

            def handle_save():
                n = name.value.strip()
                if not n:
                    error_label.set_text("Name is required")
                    return
                on_save(n, desc.value.strip(), color.value, archived_val["v"])
                dialog.close()

            ui.button("Save", on_click=handle_save).style(
                f"background-color: {Colors.ACCENT}; color: white"
            )

    dialog.open()


def show_confirm_dialog(
    title: str,
    message: str,
    on_confirm: Callable,
    confirm_text: str = "Delete",
):
    """Show a confirmation dialog."""
    with ui.dialog() as dialog, ui.card().classes("w-80"):
        ui.label(title).classes("text-lg font-bold").style(
            f"color: {Colors.TEXT_PRIMARY}"
        )
        ui.label(message).style(
            f"color: {Colors.TEXT_SECONDARY}; white-space: pre-line"
        )

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props(
                "flat"
            ).style(f"color: {Colors.TEXT_MUTED}")

            def handle_confirm():
                on_confirm()
                dialog.close()

            ui.button(confirm_text, on_click=handle_confirm).style(
                f"background-color: {Colors.DANGER}; color: white"
            )

    dialog.open()


def show_search_dialog(on_search: Callable):
    """Show search dialog."""
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Search Tasks").classes("text-lg font-bold").style(
            f"color: {Colors.TEXT_PRIMARY}"
        )

        search_input = ui.input(
            "Search by title or description...",
            value=app_state.search_query,
        ).classes("w-full").props('dark')

        with ui.row().classes("w-full justify-end gap-2 mt-2"):
            def handle_clear():
                app_state.search_query = ""
                on_search("")
                dialog.close()

            ui.button("Clear", on_click=handle_clear).props(
                "flat"
            ).style(f"color: {Colors.TEXT_MUTED}")

            ui.button("Cancel", on_click=dialog.close).props(
                "flat"
            ).style(f"color: {Colors.TEXT_MUTED}")

            def handle_search():
                query = search_input.value.strip()
                app_state.search_query = query
                on_search(query)
                dialog.close()

            ui.button("Search", on_click=handle_search).style(
                f"background-color: {Colors.ACCENT}; color: white"
            )

        search_input.on("keydown.enter", handle_search)

    dialog.open()
    search_input.run_method("focus")


def show_filter_dialog(on_apply: Callable):
    """Show filter dialog."""
    status_options = {"All Statuses": None, **STATUS_OPTIONS}
    priority_options = {"All Priorities": None, **PRIORITY_OPTIONS}

    current_status = "All Statuses"
    if app_state.filter_status:
        current_status = STATUS_DISPLAY.get(app_state.filter_status, "All Statuses")

    current_priority = "All Priorities"
    if app_state.filter_priority:
        current_priority = PRIORITY_DISPLAY.get(app_state.filter_priority, "All Priorities")

    with ui.dialog() as dialog, ui.card().classes("w-80"):
        ui.label("Filter Tasks").classes("text-lg font-bold").style(
            f"color: {Colors.TEXT_PRIMARY}"
        )

        status_sel = ui.select(
            list(status_options.keys()),
            value=current_status,
            label="Status",
        ).classes("w-full").props('dark')

        priority_sel = ui.select(
            list(priority_options.keys()),
            value=current_priority,
            label="Priority",
        ).classes("w-full").props('dark')

        with ui.row().classes("w-full justify-between mt-4"):
            def handle_clear():
                app_state.filter_status = None
                app_state.filter_priority = None
                on_apply()
                dialog.close()

            ui.button("Clear All", on_click=handle_clear).props(
                "flat"
            ).style(f"color: {Colors.TEXT_MUTED}")

            with ui.row().classes("gap-2"):
                ui.button("Cancel", on_click=dialog.close).props(
                    "flat"
                ).style(f"color: {Colors.TEXT_MUTED}")

                def handle_apply():
                    app_state.filter_status = status_options.get(status_sel.value)
                    app_state.filter_priority = priority_options.get(priority_sel.value)
                    on_apply()
                    dialog.close()

                ui.button("Apply", on_click=handle_apply).style(
                    f"background-color: {Colors.ACCENT}; color: white"
                )

    dialog.open()


def show_help_dialog():
    """Show keyboard shortcuts help."""
    shortcuts = [
        ("1", "Board view"),
        ("2", "Inbox view"),
        ("3", "Timeline view"),
        ("Ctrl+N", "New task"),
        ("Ctrl+Shift+N", "New project"),
        ("Ctrl+E", "Edit selected item"),
        ("Delete", "Delete selected item"),
        ("Ctrl+F", "Search tasks"),
        ("F", "Open filters"),
        ("A", "Toggle archived projects"),
        ("Tab", "Switch between projects"),
        ("?", "Show this help"),
    ]

    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Keyboard Shortcuts").classes("text-lg font-bold").style(
            f"color: {Colors.TEXT_PRIMARY}"
        )

        for key, description in shortcuts:
            with ui.row().classes("w-full items-center gap-3 py-1"):
                ui.label(key).style(
                    f"background-color: {Colors.SURFACE_VARIANT}; "
                    f"color: {Colors.TEXT_PRIMARY}; "
                    f"padding: 2px 10px; border-radius: 6px; "
                    f"font-size: 12px; font-weight: bold; "
                    f"min-width: 110px; text-align: center"
                )
                ui.label(description).style(
                    f"color: {Colors.TEXT_SECONDARY}; font-size: 13px"
                )

        ui.button("Close", on_click=dialog.close).props("flat").classes(
            "w-full mt-2"
        ).style(f"color: {Colors.TEXT_MUTED}")

    dialog.open()
