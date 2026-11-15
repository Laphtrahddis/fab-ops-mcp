CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE tools (
    id   INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    area TEXT NOT NULL
);

CREATE TABLE alarms (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tool_id    INT NOT NULL REFERENCES tools(id),
    code       TEXT NOT NULL,
    severity   TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
    lot_id     TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_alarms_tool_time ON alarms (tool_id, created_at DESC);

CREATE TABLE maintenance_tickets (
    id         INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tool_id    INT NOT NULL REFERENCES tools(id),
    summary    TEXT NOT NULL,
    status     TEXT NOT NULL DEFAULT 'open'
               CHECK (status IN ('open', 'in_progress', 'closed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);