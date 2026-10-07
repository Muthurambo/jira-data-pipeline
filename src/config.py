import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "DATA")

STORAGE_MODE = os.getenv("STORAGE_MODE", "local")  # local or s3
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "")
S3_BUCKET = os.getenv("S3_BUCKET", "jira-data")

# URL.create handles special characters (like @ or #) in the password safely
PG_URL = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("PG_USER", "postgres"),
    password=os.getenv("PG_PASSWORD", ""),
    host=os.getenv("PG_HOST", "localhost"),
    port=int(os.getenv("PG_PORT", "5432")),
    database=os.getenv("PG_DB", "jira_dw"),
)