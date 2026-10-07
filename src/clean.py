"""Flatten and clean raw Jira JSON into an analysis-ready Parquet file."""
import json
import os
from datetime import date

import pandas as pd

import storage

COLUMN_MAP = {
    "id": "issue_id",
    "key": "issue_key",
    "fields.summary": "summary",
    "fields.issuetype.name": "issue_type",
    "fields.status.name": "status",
    "fields.priority.name": "priority",
    "fields.assignee.displayName": "assignee",
    "fields.reporter.displayName": "reporter",
    "fields.project.key": "project_key",
    "fields.created": "created_at",
    "fields.updated": "updated_at",
    "fields.duedate": "due_date",
    "fields.resolutiondate": "resolved_at",
    "fields.labels": "labels",
    "fields.timeoriginalestimate": "original_estimate_sec",
}


def clean(raw_path):
    with open(raw_path) as f:
        issues = json.load(f)["issues"]

    df = pd.json_normalize(issues)
    # keep only the columns we need; add any the API left out (e.g. no assignee on any ticket)
    df = df.reindex(columns=list(COLUMN_MAP)).rename(columns=COLUMN_MAP)

    # 1. remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset="issue_key").reset_index(drop=True)
    print(f"Removed {before - len(df)} duplicate rows")

    # 2. fix dates
    for col in ["created_at", "updated_at", "resolved_at"]:
        df[col] = pd.to_datetime(df[col], utc=True, errors="coerce").dt.tz_localize(None)
    due = pd.to_datetime(df["due_date"], errors="coerce")
    df["due_date"] = due.dt.date

    # 3. handle missing values
    df["assignee"] = df["assignee"].fillna("Unassigned")
    df["priority"] = df["priority"].fillna("Not Set")
    df["labels"] = df["labels"].apply(lambda x: ",".join(x) if isinstance(x, list) else "")
    df["original_estimate_hours"] = (df["original_estimate_sec"] / 3600).round(1)
    df = df.drop(columns=["original_estimate_sec"])

    # 4. derived columns
    df["resolution_days"] = (df["resolved_at"] - df["created_at"]).dt.total_seconds() / 86400
    df["resolution_days"] = df["resolution_days"].round(1)
    today = pd.Timestamp.today().normalize()
    df["is_overdue"] = (df["status"] != "Done") & due.notna() & (due < today)

    return df


def run(raw_path):
    df = clean(raw_path)
    os.makedirs("data/cleaned", exist_ok=True)
    out = f"data/cleaned/jira_issues_{date.today().isoformat()}.parquet"
    df.to_parquet(out, index=False)
    storage.upload(out, f"cleaned/jira/{date.today().isoformat()}/issues.parquet")
    return df
