"""Load cleaned data into PostgreSQL as fact and dimension tables."""
import pandas as pd
from sqlalchemy import create_engine, text

from config import PG_URL


def run(df):
    engine = create_engine(PG_URL)
    with open("sql/schema.sql") as f:
        schema = f.read()

    with engine.begin() as conn:
        conn.exec_driver_sql(schema)
        conn.execute(text("TRUNCATE fact_tickets, dim_assignee, dim_status, dim_priority RESTART IDENTITY CASCADE"))

    dims = {
        "dim_assignee": ("assignee", "assignee_name", "assignee_id"),
        "dim_status": ("status", "status_name", "status_id"),
        "dim_priority": ("priority", "priority_name", "priority_id"),
    }
    fact = df.copy()
    for table, (src_col, name_col, id_col) in dims.items():
        dim = pd.DataFrame({name_col: sorted(df[src_col].dropna().unique())})
        dim.to_sql(table, engine, if_exists="append", index=False)
        lookup = pd.read_sql(f"SELECT {id_col}, {name_col} FROM {table}", engine)
        fact = fact.merge(lookup, left_on=src_col, right_on=name_col, how="left").drop(columns=[src_col, name_col])

    fact = fact.rename(columns={"reporter": "reporter"})
    fact.to_sql("fact_tickets", engine, if_exists="append", index=False)
    print(f"Loaded {len(fact)} rows into fact_tickets")
