"""NiceGUI Kanban board with SortableJS drag-and-drop."""

from nicegui import ui

from ..models import Task, TaskStatus
from ..theme import Colors, get_priority_color, get_status_color
from ..state import app_state


STATUS_LABELS = {
    TaskStatus.TODO: "To Do",
    TaskStatus.IN_PROGRESS: "In Progress",
    TaskStatus.DONE: "Done",
}

STATUS_ICONS = {
    TaskStatus.TODO: "radio_button_unchecked",
    TaskStatus.IN_PROGRESS: "pending",
    TaskStatus.DONE: "check_circle",
}


def build_kanban_board(on_task_edit, on_task_delete, on_add_task, on_filter, on_search):
    """Build the kanban board with three columns."""
    board_container = ui.column().classes("flex-1 h-screen")

    with board_container:
        # Toolbar
        with ui.row().classes("w-full items-center px-6 pt-4 pb-2 gap-2"):
            project_name = app_state.current_project.name if app_state.current_project else "No Project"
            ui.label(project_name).style(
                f"color: {Colors.TEXT_PRIMARY}; font-size: 18px; font-weight: 600"
            )
            ui.space()

            ui.button(icon="search", on_click=on_search).props(
                "flat dense round"
            ).style(f"color: {Colors.TEXT_MUTED}").tooltip("Search (Ctrl+F)")

            ui.button(icon="filter_list", on_click=on_filter).props(
                "flat dense round"
            ).style(f"color: {Colors.TEXT_MUTED}").tooltip("Filter (F)")

            # Active filters indicator
            has_filters = app_state.filter_status or app_state.filter_priority or app_state.search_query
            if has_filters:
                def clear_all():
                    app_state.clear_filters()

                ui.button("Clear filters", on_click=clear_all).props(
                    "flat dense size=sm"
                ).style(f"color: {Colors.ACCENT}; font-size: 11px")

        # Kanban columns
        if not app_state.current_project:
            with ui.column().classes("flex-1 items-center justify-center"):
                ui.label("Select or create a project to get started").style(
                    f"color: {Colors.TEXT_MUTED}; font-size: 15px"
                )
            return board_container

        columns_row = ui.row().classes("kanban-board flex-1 items-start")

        with columns_row:
            for status in [TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.DONE]:
                _build_column(status, on_task_edit, on_task_delete, on_add_task)

        # Initialize SortableJS after DOM is ready
        _init_sortable_js()

    return board_container


def _build_column(status: TaskStatus, on_task_edit, on_task_delete, on_add_task):
    """Build a single kanban column."""
    tasks = app_state.get_tasks_by_status(status)
    color = get_status_color(status.value)

    with ui.column().classes("kanban-column"):
        # Header
        with ui.row().classes("column-header w-full items-center"):
            ui.icon(STATUS_ICONS[status]).style(
                f"color: {color}; font-size: 18px"
            )
            ui.label(STATUS_LABELS[status]).style(
                f"color: {Colors.TEXT_PRIMARY}; font-size: 14px; font-weight: 600"
            ).classes("ml-2")
            ui.space()
            ui.label(str(len(tasks))).classes("column-count")

            if status == TaskStatus.TODO:
                ui.button(
                    icon="add", on_click=on_add_task,
                ).props("flat dense round size=sm").style(
                    f"color: {Colors.TEXT_MUTED}"
                ).tooltip("New task (Ctrl+N)")

        # Cards container (sortable)
        with ui.element("div").classes("column-body sortable-column").props(
            f'data-status="{status.value}"'
        ):
            for task in tasks:
                _build_task_card(task, on_task_edit, on_task_delete)


def _build_task_card(task: Task, on_edit, on_delete):
    """Build a single task card."""
    priority_color = get_priority_color(task.priority.value)

    with ui.element("div").classes("task-card").props(f'data-task-id="{task.id}"'):
        # Priority indicator + title row
        with ui.row().classes("w-full items-start no-wrap"):
            ui.element("div").style(
                f"width: 4px; min-height: 20px; border-radius: 2px; "
                f"background-color: {priority_color}; flex-shrink: 0; margin-top: 2px"
            )
            with ui.column().classes("flex-1 gap-1 ml-2"):
                ui.label(task.title).style(
                    f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; font-weight: 500"
                )
                if task.description:
                    ui.label(task.description[:80] + ("..." if len(task.description) > 80 else "")).style(
                        f"color: {Colors.TEXT_MUTED}; font-size: 11px"
                    )

        # Bottom row: metadata + actions
        with ui.row().classes("w-full items-center mt-2 gap-2"):
            # Priority badge
            ui.label(f"{task.priority_symbol} {task.priority.value}").style(
                f"color: {priority_color}; font-size: 10px; "
                f"background-color: {Colors.SURFACE_ELEVATED}; "
                f"padding: 1px 6px; border-radius: 4px"
            )

            # Due date
            if task.due_date:
                date_color = Colors.OVERDUE if task.is_overdue else Colors.TEXT_MUTED
                ui.label(f"📅 {task.due_date.strftime('%m/%d')}").style(
                    f"color: {date_color}; font-size: 10px"
                )

            ui.space()

            # Action buttons
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


def _init_sortable_js():
    """Initialize SortableJS for drag-and-drop between columns."""
    ui.add_css("""
        .task-card .task-action { opacity: 0; transition: opacity 0.15s; }
        .task-card:hover .task-action { opacity: 1 !important; }
    """)

    ui.run_javascript("""
        async function initSortable() {
            // Wait for SortableJS to load
            if (typeof Sortable === 'undefined') {
                await new Promise(resolve => {
                    const script = document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js';
                    script.onload = resolve;
                    document.head.appendChild(script);
                });
            }

            // Small delay to ensure DOM is ready
            await new Promise(r => setTimeout(r, 200));

            document.querySelectorAll('.sortable-column').forEach(column => {
                if (column._sortable) return;  // Already initialized
                column._sortable = Sortable.create(column, {
                    group: 'kanban',
                    animation: 150,
                    ghostClass: 'sortable-ghost',
                    chosenClass: 'sortable-chosen',
                    draggable: '.task-card',
                    onEnd: function(evt) {
                        const taskId = evt.item.getAttribute('data-task-id');
                        const newStatus = evt.to.getAttribute('data-status');
                        if (taskId && newStatus) {
                            emitEvent('task_moved', { task_id: parseInt(taskId), new_status: newStatus });
                        }
                    }
                });
            });
        }
        initSortable();
    """)
