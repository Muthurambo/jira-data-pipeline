"""Run the full pipeline: extract -> clean -> load -> validate.

Usage:
    python src/run_pipeline.py                 # real Jira API
    python src/run_pipeline.py --sample        # use data/sample_jira_issues.json (no Jira needed)
"""
import argparse
import sys

import clean
import extract
import load
import validate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", help="use the local sample JSON instead of the Jira API")
    args = parser.parse_args()

    raw_path = extract.run(sample_path="data/sample_jira_issues.json" if args.sample else None)
    df = clean.run(raw_path)
    load.run(df)
    failed = validate.run(df)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
