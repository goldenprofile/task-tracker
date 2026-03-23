"""Gantt chart timeline view using Apache ECharts."""

import json
from datetime import datetime, timedelta

from nicegui import ui

from ..theme import Colors, get_status_color, get_priority_color
from ..state import app_state


def build_gantt_view():
    """Build the Gantt chart timeline view."""
    gantt_container = ui.column().classes("flex-1 h-screen")

    with gantt_container:
        # Header
        with ui.row().classes("w-full items-center px-6 pt-4 pb-2 gap-3"):
            ui.icon("view_timeline").style(
                f"color: {Colors.ACCENT}; font-size: 22px"
            )
            ui.label("Timeline").style(
                f"color: {Colors.TEXT_PRIMARY}; font-size: 18px; font-weight: 600"
            )
            ui.space()

            scope_label = "All projects" if not app_state.current_project else app_state.current_project.name
            ui.label(scope_label).style(
                f"color: {Colors.TEXT_MUTED}; font-size: 13px"
            )

        tasks = app_state.get_gantt_tasks()

        if not tasks:
            # Empty state
            with ui.column().classes("flex-1 items-center justify-center"):
                ui.icon("view_timeline").style(
                    f"color: {Colors.TEXT_MUTED}; font-size: 48px; opacity: 0.3"
                )
                ui.label("No tasks with dates").style(
                    f"color: {Colors.TEXT_MUTED}; font-size: 15px"
                )
                ui.label("Add start or due dates to tasks to see them on the timeline").style(
                    f"color: {Colors.TEXT_MUTED}; font-size: 12px; opacity: 0.6"
                )
            return gantt_container

        # Legend
        with ui.row().classes("px-6 pb-2 gap-4"):
            for status_val, label in [("todo", "To Do"), ("in_progress", "In Progress"), ("done", "Done")]:
                with ui.row().classes("items-center gap-1"):
                    ui.element("div").style(
                        f"width: 12px; height: 12px; border-radius: 3px; "
                        f"background-color: {get_status_color(status_val)}"
                    )
                    ui.label(label).style(
                        f"color: {Colors.TEXT_MUTED}; font-size: 11px"
                    )

        # Chart container
        chart_id = f"gantt-chart-{id(gantt_container)}"
        chart_div = ui.element("div").style(
            f"width: 100%; flex: 1; min-height: 400px"
        )
        chart_div.props(f'id="{chart_id}"')

        # Build chart data and inject via JS
        _inject_gantt_chart(chart_id, tasks)

    return gantt_container


def _inject_gantt_chart(chart_id: str, tasks):
    """Build and inject the ECharts Gantt chart."""
    now = datetime.now()

    # Prepare data
    categories = []
    data = []

    for i, task in enumerate(tasks):
        start = task.start_date or task.created_at
        end = task.due_date or (start + timedelta(days=7))

        # Ensure end is after start
        if end <= start:
            end = start + timedelta(days=1)

        color = get_status_color(task.status.value)
        border_color = get_priority_color(task.priority.value)

        title = task.title
        if len(title) > 30:
            title = title[:28] + "..."
        categories.append(title)

        data.append({
            "value": [i, _ts(start), _ts(end)],
            "itemStyle": {
                "color": color,
                "borderColor": border_color,
                "borderWidth": 2,
                "borderRadius": 4,
            },
            "task_title": task.title,
            "task_status": task.status.value,
            "task_priority": task.priority.value,
            "start_str": start.strftime("%Y-%m-%d"),
            "end_str": end.strftime("%Y-%m-%d"),
        })

    # Find time range for the axis
    all_starts = [d["value"][1] for d in data]
    all_ends = [d["value"][2] for d in data]
    min_time = min(all_starts) - 86400000 * 2  # 2 days padding
    max_time = max(all_ends) + 86400000 * 2

    # Today marker
    today_ts = _ts(now)

    categories_json = json.dumps(categories)
    data_json = json.dumps(data)

    js = f"""
    async function initGantt() {{
        // Load ECharts if not available
        if (typeof echarts === 'undefined') {{
            await new Promise(resolve => {{
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js';
                script.onload = resolve;
                document.head.appendChild(script);
            }});
        }}

        await new Promise(r => setTimeout(r, 200));

        const el = document.getElementById('{chart_id}');
        if (!el) return;

        // Set height based on number of tasks
        const rowHeight = 40;
        const headerHeight = 80;
        const minHeight = Math.max(400, {len(data)} * rowHeight + headerHeight);
        el.style.height = minHeight + 'px';

        const chart = echarts.init(el, null, {{renderer: 'canvas'}});

        const categories = {categories_json};
        const rawData = {data_json};

        chart.setOption({{
            backgroundColor: 'transparent',
            tooltip: {{
                trigger: 'item',
                backgroundColor: '{Colors.SURFACE_ELEVATED}',
                borderColor: '{Colors.BORDER}',
                textStyle: {{ color: '{Colors.TEXT_PRIMARY}', fontSize: 12 }},
                formatter: function(params) {{
                    const d = params.data;
                    return '<b>' + d.task_title + '</b><br/>' +
                           'Status: ' + d.task_status + '<br/>' +
                           'Priority: ' + d.task_priority + '<br/>' +
                           d.start_str + ' → ' + d.end_str;
                }}
            }},
            grid: {{
                left: 200,
                right: 40,
                top: 40,
                bottom: 30,
                containLabel: false
            }},
            xAxis: {{
                type: 'time',
                position: 'top',
                min: {min_time},
                max: {max_time},
                axisLine: {{ lineStyle: {{ color: '{Colors.BORDER}' }} }},
                axisTick: {{ lineStyle: {{ color: '{Colors.BORDER}' }} }},
                axisLabel: {{
                    color: '{Colors.TEXT_MUTED}',
                    fontSize: 11,
                    formatter: function(val) {{
                        const d = new Date(val);
                        const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
                        return months[d.getMonth()] + ' ' + d.getDate();
                    }}
                }},
                splitLine: {{
                    show: true,
                    lineStyle: {{ color: '{Colors.DIVIDER}', type: 'dashed' }}
                }}
            }},
            yAxis: {{
                type: 'category',
                data: categories,
                inverse: true,
                axisLine: {{ show: false }},
                axisTick: {{ show: false }},
                axisLabel: {{
                    color: '{Colors.TEXT_SECONDARY}',
                    fontSize: 12,
                    width: 180,
                    overflow: 'truncate',
                    ellipsis: '...'
                }}
            }},
            series: [{{
                type: 'custom',
                renderItem: function(params, api) {{
                    const categoryIndex = api.value(0);
                    const start = api.coord([api.value(1), categoryIndex]);
                    const end = api.coord([api.value(2), categoryIndex]);
                    const height = api.size([0, 1])[1] * 0.55;
                    const rect = echarts.graphic.clipRectByRect(
                        {{ x: start[0], y: start[1] - height / 2, width: end[0] - start[0], height: height }},
                        {{ x: params.coordSys.x, y: params.coordSys.y, width: params.coordSys.width, height: params.coordSys.height }}
                    );
                    if (!rect) return;
                    return {{
                        type: 'rect',
                        shape: rect,
                        style: api.style({{
                            ...api.style()
                        }}),
                        styleEmphasis: {{
                            shadowBlur: 10,
                            shadowColor: 'rgba(0,0,0,0.5)'
                        }}
                    }};
                }},
                encode: {{ x: [1, 2], y: 0 }},
                data: rawData,
                clip: true
            }},
            {{
                // Today line
                type: 'line',
                markLine: {{
                    silent: true,
                    symbol: 'none',
                    lineStyle: {{
                        color: '{Colors.ACCENT}',
                        width: 2,
                        type: 'solid'
                    }},
                    label: {{
                        show: true,
                        formatter: 'Today',
                        color: '{Colors.ACCENT}',
                        fontSize: 11,
                        position: 'start'
                    }},
                    data: [{{ xAxis: {today_ts} }}]
                }},
                data: []
            }}]
        }});

        window.addEventListener('resize', () => chart.resize());
        new ResizeObserver(() => chart.resize()).observe(el);
    }}
    initGantt();
    """
    ui.run_javascript(js)


def _ts(dt: datetime) -> int:
    """Convert datetime to JS timestamp (milliseconds)."""
    return int(dt.timestamp() * 1000)
