"""
fab-ops MCP server: lets Claude look up fab equipment alarms.

Run it with:  uv run python -m fab_ops_mcp.server
"""

import os
from datetime import datetime, timedelta, timezone

import psycopg
from mcp.server import MCPServer


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://fab:fab@localhost:55432/fab_ops",
)

server = MCPServer(name="fab-ops")


@server.tool()
def get_tool_alarms(tool_name: str, hours: int = 24) -> list[dict]:
    """Get the alarms one fab tool raised in the last few hours, newest first.

    Args:
        tool_name: The tool's name, for example "ETCH-01".
        hours: How many hours back to look. Defaults to 24.
    """
    start_time = datetime.now(timezone.utc) - timedelta(hours=hours)

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT alarms.code, alarms.severity, alarms.lot_id, alarms.created_at
                FROM alarms
                JOIN tools ON tools.id = alarms.tool_id
                WHERE tools.name = %s
                  AND alarms.created_at >= %s
                ORDER BY alarms.created_at DESC
                """,
                (tool_name, start_time),
            )
            rows = cursor.fetchall()

    alarms = []
    for code, severity, lot_id, created_at in rows:
        alarm = {
            "code": code,
            "severity": severity,
            "lot_id": lot_id,
            "time": created_at.isoformat(),
        }
        alarms.append(alarm)
    return alarms


if __name__ == "__main__":
    server.run()