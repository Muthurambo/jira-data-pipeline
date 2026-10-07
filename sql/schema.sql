CREATE TABLE IF NOT EXISTS dim_assignee (
    assignee_id   SERIAL PRIMARY KEY,
    assignee_name TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS dim_status (
    status_id   SERIAL PRIMARY KEY,
    status_name TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS dim_priority (
    priority_id   SERIAL PRIMARY KEY,
    priority_name TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS fact_tickets (
    issue_id                TEXT PRIMARY KEY,
    issue_key               TEXT NOT NULL,
    summary                 TEXT,
    issue_type              TEXT,
    project_key             TEXT,
    assignee_id             INT REFERENCES dim_assignee(assignee_id),
    status_id               INT REFERENCES dim_status(status_id),
    priority_id             INT REFERENCES dim_priority(priority_id),
    reporter                TEXT,
    created_at              TIMESTAMP,
    updated_at              TIMESTAMP,
    due_date                DATE,
    resolved_at             TIMESTAMP,
    labels                  TEXT,
    original_estimate_hours NUMERIC,
    resolution_days         NUMERIC,
    is_overdue              BOOLEAN
);
CREATE TABLE IF NOT EXISTS data_quality_log (
    log_id     SERIAL PRIMARY KEY,
    run_time   TIMESTAMP DEFAULT NOW(),
    check_name TEXT,
    result     TEXT,
    details    TEXT
);
