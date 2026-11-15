"""
Seed script: fills the database with fake fab data,
so our MCP server has something realistic to query.

Run it with:  uv run python -m fab_ops_mcp.seed
"""

import os
import random
from datetime import datetime, timedelta, timezone

import psycopg


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://fab:fab@localhost:55432/fab_ops",
)

NUMBER_OF_ALARMS = 300
NUMBER_OF_DAYS = 14
CHANCE_THAT_ALARM_HAS_A_LOT = 0.8  # 80% of alarms happen while a wafer lot is in the tool

# Each tool is (tool name, fab area)
FAB_TOOLS = [
    ("ETCH-01", "Etch"),
    ("ETCH-02", "Etch"),
    ("LITHO-01", "Lithography"),
    ("LITHO-02", "Lithography"),
    ("CVD-01", "Deposition"),
    ("PVD-01", "Deposition"),
    ("CMP-01", "CMP"),
    ("IMPL-01", "Implant"),
    ("DIFF-01", "Diffusion"),
    ("METRO-01", "Metrology"),
]

# "how_common" is a weight: a bigger number means the alarm happens more often.
ALARM_TYPES = [
    {"code": "PM_DUE_SOON", "severity": "info", "how_common": 25},
    {"code": "CHAMBER_DOOR_OPEN", "severity": "info", "how_common": 15},
    {"code": "TEMP_DRIFT", "severity": "warning", "how_common": 20},
    {"code": "GAS_FLOW_DEVIATION", "severity": "warning", "how_common": 15},
    {"code": "PRESSURE_HIGH", "severity": "warning", "how_common": 10},
    {"code": "RF_REFLECTED_POWER_HIGH", "severity": "critical", "how_common": 6},
    {"code": "VACUUM_LEAK", "severity": "critical", "how_common": 5},
    {"code": "WAFER_HANDLER_FAULT", "severity": "critical", "how_common": 4},
]

# Each ticket is (tool name, summary, status)
SAMPLE_TICKETS = [
    ("ETCH-02", "RF reflected power spikes, check matching network", "open"),
    ("CVD-01", "Temperature drift on chamber B heater", "in_progress"),
    ("CMP-01", "Replaced CMP pad after scheduled PM", "closed"),
]

def pick_random_alarm_type() -> dict:
    weights = [alarm_type["how_common"] for alarm_type in ALARM_TYPES]
    chosen_alarm_types = random.choices(ALARM_TYPES, weights=weights, k=1)
    return chosen_alarm_types[0]


def pick_random_lot_id() -> str | None:
    if random.random() < CHANCE_THAT_ALARM_HAS_A_LOT:
        return f"LOT{random.randint(10000, 99999)}"
    return None


def pick_random_time_in_past_days(now: datetime, days: int) -> datetime:
    seconds_in_period = days * 24 * 60 * 60
    seconds_ago = random.randint(0, seconds_in_period)
    return now - timedelta(seconds=seconds_ago)


def build_fake_alarms(tool_ids: list[int], now: datetime) -> list[tuple]:
    fake_alarms = []
    while len(fake_alarms) < NUMBER_OF_ALARMS:
        alarm_type = pick_random_alarm_type()
        alarm_row = (
            random.choice(tool_ids),
            alarm_type["code"],
            alarm_type["severity"],
            pick_random_lot_id(),
            pick_random_time_in_past_days(now, NUMBER_OF_DAYS),
        )
        fake_alarms.append(alarm_row)
    return fake_alarms


def main() -> None:
    random.seed(42)  # same "random" data every run
    now = datetime.now(timezone.utc)

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            # 1. Start clean, so running this script twice doesn't double the data
            cursor.execute("TRUNCATE alarms, maintenance_tickets, tools RESTART IDENTITY")

            # 2. Insert tools first, because alarms and tickets point at them
            cursor.executemany(
                "INSERT INTO tools (name, area) VALUES (%s, %s)",
                FAB_TOOLS,
            )

            # 3. Ask Postgres which id it gave each tool
            cursor.execute("SELECT id, name FROM tools")
            tool_id_by_name = {}
            for tool_id, tool_name in cursor.fetchall():
                tool_id_by_name[tool_name] = tool_id

            # 4. Insert the fake alarms
            all_tool_ids = list(tool_id_by_name.values())
            fake_alarms = build_fake_alarms(all_tool_ids, now)
            cursor.executemany(
                "INSERT INTO alarms (tool_id, code, severity, lot_id, created_at) "
                "VALUES (%s, %s, %s, %s, %s)",
                fake_alarms,
            )

            # 5. Insert a few maintenance tickets
            for tool_name, summary, status in SAMPLE_TICKETS:
                cursor.execute(
                    "INSERT INTO maintenance_tickets (tool_id, summary, status) "
                    "VALUES (%s, %s, %s)",
                    (tool_id_by_name[tool_name], summary, status),
                )

    print(
        f"Seeded {len(FAB_TOOLS)} tools, {NUMBER_OF_ALARMS} alarms "
        f"over {NUMBER_OF_DAYS} days, {len(SAMPLE_TICKETS)} tickets."
    )


if __name__ == "__main__":
    main()