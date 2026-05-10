import json
import logging
import boto3
from src.etl.transformers.categorizer import categorize_jobs
from src.etl.transformers.cert_extractor import extract_certs
from src.etl.loaders.gold import aggregate_categories, load_categories_to_postgres, aggregate_certs, \
    load_certs_to_postgres
from src.etl.loaders.storage import save_to_r2
from src.config import Config
from src.etl.transformers.dedup import deduplicate_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

s3_client = boto3.client(
    "s3",
    endpoint_url=Config.R2_ENDPOINT_URL,
    aws_access_key_id=Config.R2_ACCESS_KEY_ID,
    aws_secret_access_key=Config.R2_SECRET_ACCESS_KEY,
)

bucket = Config.R2_BUCKET_NAME
connection_string = Config.DATABASE_URL

# List all bronze files
response = s3_client.list_objects_v2(Bucket=bucket, Prefix="bronze/")
bronze_files = sorted([obj["Key"] for obj in response.get("Contents", [])])

for i, key in enumerate(bronze_files):
    date = key.replace("bronze/", "").replace(".json", "")
    logger.info(f"Processing {date} ({i+1}/{len(bronze_files)})")

    try:
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        jobs = json.loads(obj["Body"].read())

        if not jobs:
            continue

        # Full pipeline
        deduped = deduplicate_jobs(jobs, connection_string, target_date=date)
        categorized = categorize_jobs(deduped)
        with_certs = extract_certs(categorized)
        save_to_r2(with_certs, date, s3_client, bucket, "silver")

        # Load both gold tables
        cert_data = aggregate_certs(with_certs)
        cat_data = aggregate_categories(with_certs)
        load_certs_to_postgres(cert_data, connection_string)
        load_categories_to_postgres(cat_data, connection_string)

    except Exception as e:
        logger.error(f"Failed for {date}: {e}")
        continue