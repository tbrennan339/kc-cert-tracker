"""
List all unique uncategorized job titles from the silver layer.

Scans every silver file in R2 and prints job titles tagged as
Uncategorized. Use this to identify gaps in categorizer patterns
and decide which titles to add or confirm as noise.

Usage: python -m scripts.check_uncategorized
"""
import json, boto3
from src.config import Config

s3 = boto3.client("s3", endpoint_url=Config.R2_ENDPOINT_URL, aws_access_key_id=Config.R2_ACCESS_KEY_ID, aws_secret_access_key=Config.R2_SECRET_ACCESS_KEY)

response = s3.list_objects_v2(Bucket=Config.R2_BUCKET_NAME, Prefix="silver/")
titles = set()
for obj_meta in sorted(response.get("Contents", []), key=lambda x: x["Key"]):
    obj = s3.get_object(Bucket=Config.R2_BUCKET_NAME, Key=obj_meta["Key"])
    jobs = json.loads(obj["Body"].read())
    for j in jobs:
        if "Uncategorized" in j.get("job_category", []):
            titles.add(j['job_title'])

for t in sorted(titles):
    print(t)

print(f"\n{len(titles)} unique uncategorized titles")

