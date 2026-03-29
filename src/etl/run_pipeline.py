import boto3

from src.etl.extractors.theirstack import extract_jobs
import datetime
import logging

from src.etl.loaders.gold import aggregate_certs, load_to_postgres
from src.etl.loaders.storage import save_to_r2
from src.etl.transformers.cert_extractor import extract_certs
from src.config import Config

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

yesterday = datetime.date.today() - datetime.timedelta(days=1)

if __name__ == "__main__":
    try:
        # Extract
        jobs = extract_jobs(api_key, 25)
        save_to_r2(jobs, str(yesterday), s3_client, r2_bucket, "bronze")

        # Transform
        jobs_with_certs = extract_certs(jobs)
        save_to_r2(jobs_with_certs, str(yesterday), s3_client, r2_bucket, "silver")

        # Load
        aggregate_data = aggregate_certs(jobs_with_certs)
        load_to_postgres(aggregate_data, connection_string)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


