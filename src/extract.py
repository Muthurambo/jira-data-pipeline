"""Extract issues from the Jira Cloud REST API (token pagination, auth, rate-limit retry)."""
import json
import os
import time
from datetime import date

import requests

import storage
from config import JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY

FIELDS = "summary,issuetype,status,priority,assignee,reporter,project,created,updated,duedate,resolutiondate,labels,timeoriginalestimate"
MAX_RETRIES = 5


def _get(session, url, params):
    """GET with retry on rate limits (429) and server errors (5xx)."""
    for attempt in range(1, MAX_RETRIES + 1):
        resp = session.get(url, params=params, timeout=30)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 2 ** attempt))
            print(f"Rate limited. Waiting {wait}s (attempt {attempt}/{MAX_RETRIES})")
            time.sleep(wait)
            continue
        if resp.status_code >= 500:
            wait = 2 ** attempt
            print(f"Server error {resp.status_code}. Retrying in {wait}s")
            time.sleep(wait)
            continue
        resp.raise_for_status()  # 401/403/404 etc. raise immediately
        return resp.json()
    raise RuntimeError("Jira API failed after maximum retries")


def fetch_all_issues():
    session = requests.Session()
    session.auth = (JIRA_EMAIL, JIRA_API_TOKEN)  # basic auth with API token
    session.headers.update({"Accept": "application/json"})

    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    params = {
        "jql": f"project = {JIRA_PROJECT_KEY} ORDER BY created ASC",
        "fields": FIELDS,
        "maxResults": 100,
    }
    issues, page = [], 1
    while True:
        data = _get(session, url, params)
        batch = data.get("issues", [])
        issues.extend(batch)
        print(f"Page {page}: fetched {len(batch)} issues (total {len(issues)})")
        token = data.get("nextPageToken")
        if data.get("isLast", True) or not token:
            break
        params["nextPageToken"] = token  # cursor-based pagination
        page += 1
    return issues


def run(sample_path=None):
    """Return path of the saved raw JSON file. Use sample_path to skip the API."""
    today = date.today().isoformat()
    os.makedirs("data/raw", exist_ok=True)
    raw_path = f"data/raw/jira_issues_{today}.json"

    if sample_path:
        with open(sample_path) as f:
            payload = json.load(f)
    else:
        payload = {"total": 0, "issues": fetch_all_issues()}
        payload["total"] = len(payload["issues"])

    with open(raw_path, "w") as f:
        json.dump(payload, f)
    storage.upload(raw_path, f"raw/jira/{today}/issues.json")
    return raw_path
