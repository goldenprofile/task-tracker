"""Theme configuration for Task Tracker — modern neutral dark theme."""

from nicegui import ui


class Colors:
    """Application color scheme (Linear / Notion-inspired neutral dark)."""

    # Background colors — neutral grays with subtle elevation
    BACKGROUND = "#0a0a0b"
    SURFACE = "#131316"
    SURFACE_VARIANT = "#1c1c21"
    SURFACE_ELEVATED = "#232329"

    # Text colors
    TEXT_PRIMARY = "#ececef"
    TEXT_SECONDARY = "#8b8b93"
    TEXT_MUTED = "#55555c"

    # Priority colors — modern, slightly desaturated
    PRIORITY_HIGH = "#f87171"     # soft red
    PRIORITY_MEDIUM = "#fbbf24"   # amber
    PRIORITY_LOW = "#34d399"      # emerald

    # Status colors
    STATUS_TODO = "#6b7280"       # cool gray
    STATUS_IN_PROGRESS = "#818cf8"  # indigo
    STATUS_DONE = "#34d399"       # emerald

    # Project colors — vibrant but balanced palette
    PROJECT_COLORS = {
        "blue": "#60a5fa",
        "green": "#34d399",
        "red": "#f87171",
        "yellow": "#fbbf24",
        "purple": "#a78bfa",
        "cyan": "#22d3ee",
        "orange": "#fb923c",
        "pink": "#f472b6",
    }

    # UI colors
    ACCENT = "#818cf8"            # indigo — main accent
    ACCENT_HOVER = "#6366f1"      # indigo darker
    ACCENT_SUBTLE = "#2e2e5e"     # indigo bg tint for badges
    DIVIDER = "#1f1f24"
    HOVER = "#1f1f26"
    SELECTED = "#262630"
    BORDER = "#2a2a33"
    OVERDUE = "#ef4444"
    ARCHIVED = "#6b7280"

    # Semantic
    DANGER = "#ef4444"
    DANGER_HOVER = "#dc2626"
    SUCCESS = "#34d399"


class Styles:
    """Application styles."""

    RADIUS_SMALL = 6
    RADIUS_MEDIUM = 10
    RADIUS_LARGE = 14

    SPACING_SMALL = 8
    SPACING_MEDIUM = 16
    SPACING_LARGE = 24

    SIDEBAR_WIDTH = 280
    CARD_MIN_HEIGHT = 80
    COLUMN_MIN_WIDTH = 300

    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_XS = 10
    FONT_SIZE_SM = 11
    FONT_SIZE_BASE = 13
    FONT_SIZE_LG = 15
    FONT_SIZE_XL = 18
    FONT_SIZE_2XL = 22


def get_priority_color(priority: str) -> str:
    """Get color for task priority."""
    colors = {
        "high": Colors.PRIORITY_HIGH,
        "medium": Colors.PRIORITY_MEDIUM,
        "low": Colors.PRIORITY_LOW,
    }
    return colors.get(priority, Colors.PRIORITY_MEDIUM)


def get_status_color(status: str) -> str:
    """Get color for task status."""
    colors = {
        "todo": Colors.STATUS_TODO,
        "in_progress": Colors.STATUS_IN_PROGRESS,
        "done": Colors.STATUS_DONE,
    }
    return colors.get(status, Colors.STATUS_TODO)


def get_project_color(color: str) -> str:
    """Get color for project."""
    return Colors.PROJECT_COLORS.get(color, Colors.PROJECT_COLORS["blue"])


def inject_theme_css():
    """Inject global CSS for the dark theme."""
    ui.add_css(f"""
        :root {{
            --bg: {Colors.BACKGROUND};
            --surface: {Colors.SURFACE};
            --surface-variant: {Colors.SURFACE_VARIANT};
            --surface-elevated: {Colors.SURFACE_ELEVATED};
            --text-primary: {Colors.TEXT_PRIMARY};
            --text-secondary: {Colors.TEXT_SECONDARY};
            --text-muted: {Colors.TEXT_MUTED};
            --accent: {Colors.ACCENT};
            --accent-hover: {Colors.ACCENT_HOVER};
            --border: {Colors.BORDER};
            --divider: {Colors.DIVIDER};
            --hover: {Colors.HOVER};
            --selected: {Colors.SELECTED};
            --danger: {Colors.DANGER};
        }}

        body {{
            background-color: {Colors.BACKGROUND} !important;
            color: {Colors.TEXT_PRIMARY};
            font-family: '{Styles.FONT_FAMILY}', system-ui, sans-serif;
        }}

        .q-page {{
            background-color: {Colors.BACKGROUND} !important;
        }}

        /* Scrollbar styling */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: transparent;
        }}
        ::-webkit-scrollbar-thumb {{
            background: {Colors.BORDER};
            border-radius: 3px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {Colors.TEXT_MUTED};
        }}

        /* Sidebar */
        .sidebar {{
            background-color: {Colors.SURFACE};
            width: {Styles.SIDEBAR_WIDTH}px;
            min-width: {Styles.SIDEBAR_WIDTH}px;
            border-right: 1px solid {Colors.DIVIDER};
            height: 100vh;
            overflow-y: auto;
        }}

        .project-item {{
            padding: 10px 16px;
            cursor: pointer;
            border-radius: {Styles.RADIUS_MEDIUM}px;
            margin: 2px 8px;
            transition: background-color 0.15s;
        }}
        .project-item:hover {{
            background-color: {Colors.HOVER};
        }}
        .project-item.selected {{
            background-color: {Colors.SELECTED};
        }}

        /* Kanban */
        .kanban-board {{
            flex: 1;
            overflow-x: auto;
            padding: 24px;
            gap: 20px;
        }}

        .kanban-column {{
            background-color: {Colors.SURFACE};
            border-radius: {Styles.RADIUS_LARGE}px;
            min-width: {Styles.COLUMN_MIN_WIDTH}px;
            width: {Styles.COLUMN_MIN_WIDTH}px;
            border: 1px solid {Colors.DIVIDER};
            display: flex;
            flex-direction: column;
            max-height: calc(100vh - 48px);
        }}

        .column-header {{
            padding: 16px 16px 12px;
            border-bottom: 1px solid {Colors.DIVIDER};
        }}

        .column-body {{
            padding: 8px;
            overflow-y: auto;
            flex: 1;
            min-height: 100px;
        }}

        /* Task cards */
        .task-card {{
            background-color: {Colors.SURFACE_VARIANT};
            border: 1px solid {Colors.BORDER};
            border-radius: {Styles.RADIUS_MEDIUM}px;
            padding: 12px;
            margin-bottom: 8px;
            cursor: grab;
            transition: border-color 0.15s, box-shadow 0.15s;
        }}
        .task-card:hover {{
            border-color: {Colors.ACCENT};
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}
        .task-card.sortable-ghost {{
            opacity: 0.4;
        }}
        .task-card.sortable-chosen {{
            box-shadow: 0 4px 16px rgba(0,0,0,0.4);
        }}

        /* Dialogs */
        .q-dialog .q-card {{
            background-color: {Colors.SURFACE} !important;
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER};
            border-radius: {Styles.RADIUS_LARGE}px;
        }}

        /* Input overrides */
        .q-field--dark .q-field__control {{
            background-color: {Colors.SURFACE_VARIANT} !important;
        }}

        /* Badge for column counts */
        .column-count {{
            background-color: {Colors.SURFACE_VARIANT};
            color: {Colors.TEXT_MUTED};
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
        }}
    """)
