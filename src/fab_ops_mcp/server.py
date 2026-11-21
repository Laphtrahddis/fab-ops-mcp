"""
fab-ops MCP server: lets Claude look up fab equipment alarms.

Run it with:  uv run python -m fab_ops_mcp.server
"""

import os
from datetime import datetime, timedelta, timezone

import psycopg
from mcp.server import MCPServer

from typing import Literal


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://fab:fab@localhost:55432/fab_ops",
)

server = MCPServer(name="fab-ops")


@server.tool()
def get_tool_alarms(
    tool_name: str,
    hours: int = 24,
    severity: Literal["info", "warning", "critical"] | None = None,
) -> list[dict]:
    """Get the alarms one fab tool raised in the last few hours, newest first.

    Args:
        tool_name: The tool's name, for example "ETCH-01".
        hours: How many hours back to look. Defaults to 24.
        severity: Only return alarms of this severity. Leave empty for all.
    """
    start_time = datetime.now(timezone.utc) - timedelta(hours=hours)

    sql = """
        SELECT alarms.code, alarms.severity, alarms.lot_id, alarms.created_at
        FROM alarms
        JOIN tools ON tools.id = alarms.tool_id
        WHERE tools.name = %s
          AND alarms.created_at >= %s
    """
    values = [tool_name, start_time]

    if severity is not None:
        sql += " AND alarms.severity = %s"
        values.append(severity)

    sql += " ORDER BY alarms.created_at DESC"

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, values)
            rows = cursor.fetchall()

    alarms = []
    for code, severity_value, lot_id, created_at in rows:
        alarm = {
            "code": code,
            "severity": severity_value,
            "lot_id": lot_id,
            "time": created_at.isoformat(),
        }
        alarms.append(alarm)
    return alarms


@server.tool()
def list_tools() -> list[dict]:
    """List every piece of fab equipment (name and fab area, e.g. ETCH-01 in Etch).

    Use this to find valid equipment names before calling get_tool_alarms.
    """
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT tools.name, tools.area, tools.id
                FROM tools
                ORDER BY tools.name
                """
            )
            rows = cursor.fetchall()

    fab_tools = []
    for name, area, tool_id in rows:
        fab_tool = {
            "name": name,
            "area": area,
            "id": tool_id,
        }
        fab_tools.append(fab_tool)
    return fab_tools


if __name__ == "__main__":
    server.run()
