"""
Look up a job description by date and title keyword.

Searches silver files first (includes category and cert data),
falls back to bronze if not found. Prints the full job description
and metadata.

Usage: python -m scripts.lookup_job <date> <title keyword>
Example: python -m scripts.lookup_job 2026-03-15 'network engineer'
"""
import json
import sys
import boto3
from src.config import Config

if len(sys.argv) < 3:
    print("Usage: python -m scripts.lookup_job <date> <title keyword>")
    print("Example: python -m scripts.lookup_job 2026-03-15 'network engineer'")
    sys.exit(1)

date = sys.argv[1]
keyword = sys.argv[2].lower()

s3 = boto3.client(
    "s3",
    endpoint_url=Config.R2_ENDPOINT_URL,
    aws_access_key_id=Config.R2_ACCESS_KEY_ID,
    aws_secret_access_key=Config.R2_SECRET_ACCESS_KEY,
)

# Try silver first, fall back to bronze
for layer in ["silver", "bronze"]:
    try:
        obj = s3.get_object(Bucket=Config.R2_BUCKET_NAME, Key=f"{layer}/{date}.json")
        jobs = json.loads(obj["Body"].read())
        matches = [j for j in jobs if keyword in j.get("job_title", "").lower()]

        if not matches:
            continue

        for j in matches:
            print(f"{'='*60}")
            print(f"Title:    {j.get('job_title')}")
            print(f"Company:  {j.get('company')}")
            print(f"Location: {j.get('location')}")
            print(f"Source:   {layer}/{date}.json")
            if j.get('job_category'):
                print(f"Category: {j.get('job_category')}")
            if j.get('certs_found'):
                print(f"Certs:    {j.get('certs_found')}")
            print(f"{'─'*60}")
            print(j.get("description", "No description available"))
            print()

        sys.exit(0)

    except Exception:
        continue

print(f"No jobs matching '{keyword}' found on {date}")