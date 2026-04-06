import time
import boto3
from src.etl.extractors.theirstack import extract_jobs
import datetime
import logging
from src.etl.loaders.gold import aggregate_certs, load_to_postgres
from src.etl.loaders.storage import save_to_r2
from src.etl.transformers.cert_extractor import extract_certs
from src.config import Config
from src.etl.transformers.dedup import deduplicate_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

r2_bucket = Config.R2_BUCKET_NAME
s3_client = boto3.client(
    "s3",
    endpoint_url=Config.R2_ENDPOINT_URL,
    aws_access_key_id=Config.R2_ACCESS_KEY_ID,
    aws_secret_access_key=Config.R2_SECRET_ACCESS_KEY,
)

api_key = Config.THEIRSTACK_API_KEY
connection_string = Config.DATABASE_URL

# Configure backfill range
start = datetime.date(2026, 1, 1)  # First date to backfill
end = datetime.date.today() - datetime.timedelta(days=1)  # Yesterday

dates = [start + datetime.timedelta(days=i) for i in range((end - start).days + 1)]

consecutive_failures = 0

for i, date in enumerate(dates):
    logger.info(f"Processing {date} ({i+1}/{len(dates)})")
    try:
        # Extract
        jobs = extract_jobs(api_key, 25, date)
        save_to_r2(jobs, str(date), s3_client, r2_bucket, "bronze")

        # Transform
        deduped_jobs = deduplicate_jobs(jobs, connection_string, target_date=str(date))
        jobs_with_certs = extract_certs(deduped_jobs)
        save_to_r2(jobs_with_certs, str(date), s3_client, r2_bucket, "silver")

        # Load
        aggregate_data = aggregate_certs(jobs_with_certs)
        load_to_postgres(aggregate_data, connection_string)

        # Wait
        time.sleep(2)
        consecutive_failures = 0

    except Exception as e:
        consecutive_failures += 1
        logger.error(f"Pipeline failed for {date}: {e}")
        if consecutive_failures >= 3:
            logger.error(f"3 consecutive failures — stopping. Last successful date: check logs above.")
            break
        continue