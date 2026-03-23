"""Inbox view for quick task capture."""

from nicegui import ui

from ..models import TaskPriority
from ..theme import Colors, get_priority_color, get_status_color
from ..state import app_state


def build_inbox_view(on_task_edit, on_task_delete, on_assign_project):
    """Build the inbox quick-capture view."""
    inbox_container = ui.column().classes("flex-1 h-screen")

    with inbox_container:
        # Header
        with ui.row().classes("w-full items-center px-6 pt-4 pb-2"):
            ui.icon("inbox").style(
                f"color: {Colors.ACCENT}; font-size: 22px"
            )
            ui.label("Inbox").style(
                f"color: {Colors.TEXT_PRIMARY}; font-size: 18px; font-weight: 600"
            )
            ui.space()
            inbox_tasks = app_state.get_inbox_tasks()
            ui.label(f"{len(inbox_tasks)} tasks").style(
                f"color: {Colors.TEXT_MUTED}; font-size: 13px"
            )

        # Quick-add bar
        with ui.row().classes("w-full px-6 pb-2 gap-2 items-center"):
            quick_input = ui.input(
                placeholder="Quick add task... press Enter",
            ).classes("flex-1").props("dark dense outlined")
            quick_input.style(
                f"font-size: 14px"
            )

            priority_select = ui.select(
                {"low": "Low", "medium": "Medium", "high": "High"},
                value="medium",
            ).props("dark dense outlined").style("min-width: 100px")

            def add_task():
                title = quick_input.value.strip()
                if not title:
                    return
                p = TaskPriority(priority_select.value)
                app_state.create_inbox_task(title, p)
                quick_input.value = ""

            quick_input.on("keydown.enter", add_task)
            ui.button(icon="add", on_click=add_task).props(
                "dense round"
            ).style(f"background-color: {Colors.ACCENT}; color: white")

        # Task list
        with ui.scroll_area().classes("flex-1 w-full"):
            with ui.column().classes("w-full px-6 gap-2 pb-4"):
                if not inbox_tasks:
                    with ui.column().classes("w-full items-center py-12"):
                        ui.icon("inbox").style(
                            f"color: {Colors.TEXT_MUTED}; font-size: 48px; opacity: 0.3"
                        )
                        ui.label("Inbox is empty").style(
                            f"color: {Colors.TEXT_MUTED}; font-size: 15px"
                        )
                        ui.label("Type above and press Enter to add tasks").style(
                            f"color: {Colors.TEXT_MUTED}; font-size: 12px; opacity: 0.6"
                        )
                else:
                    for task in inbox_tasks:
                        _build_inbox_card(task, on_task_edit, on_task_delete, on_assign_project)

    return inbox_container


def _build_inbox_card(task, on_edit, on_delete, on_assign):
    """Build a single inbox task card."""
    priority_color = get_priority_color(task.priority.value)
    status_color = get_status_color(task.status.value)

    with ui.element("div").classes("task-card").style("cursor: default"):
        with ui.row().classes("w-full items-center no-wrap gap-3"):
            # Priority bar
            ui.element("div").style(
                f"width: 4px; min-height: 36px; border-radius: 2px; "
                f"background-color: {priority_color}; flex-shrink: 0"
            )

            # Status icon (clickable to cycle)
            status_icon = ui.icon(
                "check_circle" if task.status.value == "done"
                else "pending" if task.status.value == "in_progress"
                else "radio_button_unchecked"
            ).style(f"color: {status_color}; font-size: 20px; cursor: pointer")

            def cycle_status(t=task):
                from ..models import TaskStatus
                order = [TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.DONE]
                idx = order.index(t.status)
                new_status = order[(idx + 1) % len(order)]
                app_state.update_task(t.id, status=new_status)

            status_icon.on("click", cycle_status)

            # Title and meta
            with ui.column().classes("flex-1 gap-0"):
                title_style = f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; font-weight: 500"
                if task.status.value == "done":
                    title_style += "; text-decoration: line-through; opacity: 0.5"
                ui.label(task.title).style(title_style)

                if task.description:
                    ui.label(task.description[:100]).style(
                        f"color: {Colors.TEXT_MUTED}; font-size: 11px"
                    )

            # Priority badge
            ui.label(f"{task.priority_symbol} {task.priority.value}").style(
                f"color: {priority_color}; font-size: 10px; "
                f"background-color: {Colors.SURFACE_ELEVATED}; "
                f"padding: 1px 6px; border-radius: 4px"
            )

            # Assign to project
            if app_state.projects:
                project_options = {p.id: p.name for p in app_state.projects}

                def assign(e, t=task):
                    if e.value:
                        on_assign(t, e.value)

                ui.select(
                    project_options,
                    value=None,
                    on_change=assign,
                ).props("dark dense borderless").style(
                    f"min-width: 120px; font-size: 11px; color: {Colors.TEXT_MUTED}"
                ).tooltip("Assign to project")

            # Edit / Delete
            ui.button(
                icon="edit", on_click=lambda t=task: on_edit(t),
            ).props("flat dense round size=xs").style(
                f"color: {Colors.TEXT_MUTED}; opacity: 0.5"
            ).classes("task-action")

            ui.button(
                icon="close", on_click=lambda t=task: on_delete(t),
            ).props("flat dense round size=xs").style(
                f"color: {Colors.TEXT_MUTED}; opacity: 0.5"
            ).classes("task-action")
