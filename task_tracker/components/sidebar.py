"""NiceGUI sidebar with project list."""

from nicegui import ui

from ..models import Project, ViewMode
from ..theme import Colors, get_project_color
from ..state import app_state


def build_sidebar(
    on_new_project,
    on_edit_project,
    on_delete_project,
    on_help,
    refresh_board,
):
    """Build the sidebar with project list."""
    with ui.column().classes("sidebar p-0"):
        # Navigation
        with ui.column().classes("w-full px-1 pt-3 pb-0 gap-0"):
            nav_items = [
                (ViewMode.KANBAN, "view_kanban", "Board"),
                (ViewMode.INBOX, "inbox", "Inbox"),
                (ViewMode.GANTT, "view_timeline", "Timeline"),
            ]
            for view, icon, label in nav_items:
                is_active = app_state.current_view == view
                cls = "nav-item" + (" selected" if is_active else "")
                with ui.element("div").classes(cls) as nav:
                    def on_nav_click(v=view):
                        app_state.switch_view(v)
                    nav.on("click", on_nav_click)

                    with ui.row().classes("w-full items-center no-wrap gap-2"):
                        icon_color = Colors.ACCENT if is_active else Colors.TEXT_MUTED
                        ui.icon(icon).style(f"color: {icon_color}; font-size: 18px")
                        text_color = Colors.TEXT_PRIMARY if is_active else Colors.TEXT_SECONDARY
                        ui.label(label).style(f"color: {text_color}; font-size: 13px; font-weight: 500")

                        if view == ViewMode.INBOX:
                            count = len(app_state.get_inbox_tasks())
                            if count > 0:
                                ui.label(str(count)).classes("column-count")

        ui.element("div").classes("nav-divider")

        # Header
        with ui.row().classes("w-full items-center px-4 pt-2 pb-2"):
            ui.label("PROJECTS").style(
                f"color: {Colors.TEXT_MUTED}; font-size: 11px; "
                f"letter-spacing: 1.5px; font-weight: 600"
            )
            ui.space()

            def toggle_archived():
                app_state.show_archived = not app_state.show_archived
                app_state.load_projects()
                app_state.notify_update()

            archive_btn = ui.button(
                icon="archive", on_click=toggle_archived,
            ).props("flat dense round size=sm").tooltip("Toggle archived")
            archive_btn.style(f"color: {Colors.TEXT_MUTED}")

            help_btn = ui.button(
                icon="help_outline", on_click=on_help,
            ).props("flat dense round size=sm").tooltip("Keyboard shortcuts")
            help_btn.style(f"color: {Colors.TEXT_MUTED}")

        # Project list container
        project_list_container = ui.column().classes(
            "w-full flex-1 overflow-y-auto px-1 gap-0"
        )

        def render_projects():
            project_list_container.clear()
            with project_list_container:
                for project in app_state.projects:
                    _build_project_item(
                        project,
                        on_edit=on_edit_project,
                        on_delete=on_delete_project,
                        refresh_all=refresh_board,
                    )

        # Initial render
        render_projects()

        # Store render function for external refresh
        project_list_container.render_projects = render_projects

        # New project button at bottom
        ui.space()
        with ui.row().classes("w-full px-4 pb-4"):
            ui.button(
                "+ New Project", on_click=on_new_project,
            ).classes("w-full").style(
                f"background-color: {Colors.SURFACE_VARIANT}; "
                f"color: {Colors.TEXT_SECONDARY}; "
                f"border: 1px dashed {Colors.BORDER}; "
                f"border-radius: 10px"
            ).props("flat")

    return project_list_container


def _build_project_item(project: Project, on_edit, on_delete, refresh_all):
    """Build a single project item in the sidebar."""
    is_selected = (
        app_state.current_project and app_state.current_project.id == project.id
    )
    color = get_project_color(project.color)

    item_classes = "project-item" + (" selected" if is_selected else "")

    with ui.element("div").classes(item_classes) as item:
        def select_project(p=project):
            app_state.select_project(p)

        item.on("click", select_project)

        with ui.row().classes("w-full items-center no-wrap"):
            # Color dot
            ui.element("div").style(
                f"width: 10px; height: 10px; border-radius: 50%; "
                f"background-color: {color}; flex-shrink: 0"
            )

            # Name + stats
            with ui.column().classes("flex-1 gap-0 ml-3"):
                name_style = f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; font-weight: 500"
                if project.archived:
                    name_style += f"; opacity: 0.5"
                ui.label(project.name).style(name_style).classes("truncate")

                stats = f"{project.completed_count}/{project.task_count}"
                ui.label(stats).style(
                    f"color: {Colors.TEXT_MUTED}; font-size: 11px"
                )

            # Edit/delete buttons (only if selected)
            if is_selected:
                ui.button(
                    icon="edit", on_click=lambda p=project: on_edit(p),
                ).props("flat dense round size=xs").style(
                    f"color: {Colors.TEXT_MUTED}"
                )
                ui.button(
                    icon="delete", on_click=lambda p=project: on_delete(p),
                ).props("flat dense round size=xs").style(
                    f"color: {Colors.TEXT_MUTED}"
                )
