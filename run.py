#!/usr/bin/env python3
"""Entry point for Task Tracker application."""

from task_tracker.app import main_page  # noqa: F401 — registers the page
from nicegui import ui

if __name__ == "__main__":
    ui.run(
        title="Task Tracker",
        dark=True,
        reload=False,
        port=8080,
    )
