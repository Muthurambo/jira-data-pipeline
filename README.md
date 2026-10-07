# Jira Ticket Data Pipeline and Dashboard

An end-to-end data engineering project that extracts ticket data from the Jira Cloud REST API,
stores raw and cleaned files in a layered data lake (raw / cleaned), loads fact and dimension
tables into PostgreSQL with data quality checks, and feeds a Power BI dashboard.
Every tool used is free.

## Architecture
Jira Cloud REST API -> Python (extract) -> data lake raw/ -> Pandas (clean) -> data lake cleaned/ (Parquet)
-> PostgreSQL (fact + dimension tables) -> Data quality checks -> Power BI dashboard

## Tools (all free)
Python, Pandas, Requests, PyArrow (Parquet), SQLAlchemy, PostgreSQL, pgAdmin,
Jira Cloud Free, Power BI Desktop, Git, GitHub, Windows Task Scheduler / cron

## Setup
1. Install Python 3.10+, PostgreSQL, Git.
2. Create a free Jira Cloud site at atlassian.com and a project (note the project key, e.g. DATA).
3. Create an API token: Atlassian account > Security > Create and manage API tokens.
4. In pgAdmin, create a database named `jira_dw`.
5. `pip install -r requirements.txt`
6. Copy `.env.example` to `.env` and fill in your values.

## Run
- Optional: `python src/seed_jira.py` creates up to 50 sample tickets in your Jira project.
  Move some tickets to In Progress / Done on the board for variety.
- Full pipeline with the real Jira API: `python src/run_pipeline.py`
- No Jira yet? Practice with sample data: `python src/run_pipeline.py --sample`
- Analysis queries: `sql/analysis.sql`

## Features
- Cursor-based pagination (nextPageToken) for the Jira search API
- API token authentication
- Retry with Retry-After on HTTP 429 and exponential backoff on 5xx errors
- Raw / cleaned data lake layers with date partitions (data/lake/). Optional S3 mode: set STORAGE_MODE=s3 in .env for any S3-compatible service
- Cleaning: flatten nested JSON, deduplicate, standardize dates, handle nulls
- Star schema: fact_tickets, dim_assignee, dim_status, dim_priority
- Validation: row counts, duplicates, nulls, date logic, results logged to data_quality_log

## Scheduling
- Windows: Task Scheduler > Create Basic Task > Daily > `python src/run_pipeline.py`
- Mac/Linux cron: `0 8 * * * cd /path/to/project && python src/run_pipeline.py`

## Dashboard (Power BI Desktop)
Get Data > PostgreSQL database > load the 4 tables. Build visuals:
tickets by status, workload per assignee, overdue tickets, tickets created per week.
Save screenshots in a `docs/` folder and link them here.
