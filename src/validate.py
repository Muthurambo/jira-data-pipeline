"""Data quality checks. Results are printed and saved to data_quality_log."""
import pandas as pd
from sqlalchemy import create_engine, text

from config import PG_URL


def run(df):
    engine = create_engine(PG_URL)
    fact = pd.read_sql("SELECT * FROM fact_tickets", engine)

    checks = [
        ("row_count_matches_source", len(fact) == len(df), f"source={len(df)}, loaded={len(fact)}"),
        ("no_duplicate_issue_keys", fact["issue_key"].is_unique, f"duplicates={fact['issue_key'].duplicated().sum()}"),
        ("no_null_issue_key", fact["issue_key"].notna().all(), f"nulls={fact['issue_key'].isna().sum()}"),
        ("no_null_status", fact["status_id"].notna().all(), f"nulls={fact['status_id'].isna().sum()}"),
        ("no_null_created_at", fact["created_at"].notna().all(), f"nulls={fact['created_at'].isna().sum()}"),
        ("resolved_not_before_created",
         ((fact["resolved_at"].isna()) | (fact["resolved_at"] >= fact["created_at"])).all(), "resolved_at >= created_at"),
    ]

    failed = 0
    with engine.begin() as conn:
        for name, ok, details in checks:
            result = "PASS" if ok else "FAIL"
            failed += 0 if ok else 1
            print(f"[{result}] {name} ({details})")
            conn.execute(
                text("INSERT INTO data_quality_log (check_name, result, details) VALUES (:n, :r, :d)"),
                {"n": name, "r": result, "d": details},
            )
    print(f"Validation finished: {len(checks) - failed} passed, {failed} failed")
    return failed
