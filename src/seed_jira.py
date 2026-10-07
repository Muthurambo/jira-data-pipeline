"""Optional: create sample tickets in your FREE Jira Cloud project from the sample CSV.

Statuses cannot be set at creation time in Jira. After seeding, move a few tickets
to In Progress / Done manually on the board so your data has variety.
"""
import csv
import time

import requests

from config import JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY

LIMIT = 50
url = f"{JIRA_BASE_URL}/rest/api/3/issue"
auth = (JIRA_EMAIL, JIRA_API_TOKEN)

with open("data/jira_tickets.csv") as f:
    rows = list(csv.DictReader(f))

seen, created = set(), 0
for row in rows:
    if row["key"] in seen:
        continue
    seen.add(row["key"])
    payload = {"fields": {
        "project": {"key": JIRA_PROJECT_KEY},
        "summary": row["summary"],
        "issuetype": {"name": "Task"},
        "labels": [l for l in row["labels"].split(";") if l],
    }}
    resp = requests.post(url, json=payload, auth=auth, timeout=30)
    if resp.status_code == 429:
        time.sleep(int(resp.headers.get("Retry-After", 5)))
        resp = requests.post(url, json=payload, auth=auth, timeout=30)
    if resp.ok:
        created += 1
        print("Created", resp.json()["key"])
    else:
        print("Failed:", resp.status_code, resp.text[:200])
    if created >= LIMIT:
        break
    time.sleep(0.3)
print(f"Done. Created {created} tickets.")
