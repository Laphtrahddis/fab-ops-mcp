"""
fab-ops MCP server: lets Claude look up fab equipment alarms.

Run it with:  uv run python -m fab_ops_mcp.server
"""

import os
from datetime import datetime, timedelta, timezone

import psycopg
from mcp.server import MCPServer

from typing import Literal

from fastembed import TextEmbedding
from pgvector.psycopg import register_vector

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://fab:fab@localhost:55432/fab_ops",
)

server = MCPServer(name="fab-ops")
embedding_model = TextEmbedding("BAAI/bge-small-en-v1.5")


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


@server.tool()
def top_noisy_tools(days: int = 7, limit: int = 5) -> list[dict]:
    """Rank fab tools by how many alarms they raised in the last few days, noisiest first.

    Use this for questions like "which tools alarmed most this week?".
    Each result also counts how many of those alarms were critical.

    Args:
        days: How many days back to look. Defaults to 7.
        limit: How many tools to return. Defaults to 5.
    """
    start_time = datetime.now(timezone.utc) - timedelta(days=days)

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT tools.name,
                       tools.area,
                       count(*) AS alarm_count,
                       count(*) FILTER (WHERE alarms.severity = 'critical') AS critical_count
                FROM alarms
                JOIN tools ON tools.id = alarms.tool_id
                WHERE alarms.created_at >= %s
                GROUP BY tools.name, tools.area
                ORDER BY alarm_count DESC
                LIMIT %s
                """,
                [start_time, limit],
            )
            rows = cursor.fetchall()

    noisy_tools = []
    for name, area, alarm_count, critical_count in rows:
        noisy_tool = {
            "name": name,
            "area": area,
            "alarm_count": alarm_count,
            "critical_count": critical_count,
        }
        noisy_tools.append(noisy_tool)
    return noisy_tools


@server.tool()
def search_manual(question: str, top_k: int = 3) -> list[dict]:
    """Search the fab equipment manuals by meaning and return the most relevant pages.

    Use this for "how do I fix / what causes / what are the steps for" questions
    about alarms, maintenance or equipment. Answer only from the returned pages,
    and always cite the manual title and page number you used.

    Args:
        question: The engineer's question in plain English.
        top_k: How many pages to return. Defaults to 3.
    """
    question_embedding = list(embedding_model.query_embed([question]))[0]

    with psycopg.connect(DATABASE_URL) as connection:
        register_vector(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT manual_title,
                       page_number,
                       content,
                       1 - (embedding <=> %s) AS similarity
                FROM manual_pages
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (question_embedding, question_embedding, top_k),
            )
            rows = cursor.fetchall()

    matching_pages = []
    for manual_title, page_number, content, similarity in rows:
        matching_page = {
            "manual": manual_title,
            "page": page_number,
            "similarity": round(similarity, 3),
            "text": content,
        }
        matching_pages.append(matching_page)
    return matching_pages

if __name__ == "__main__":
    server.run()
