import json
import logging

logger = logging.getLogger(__name__)


def save_to_r2(data: list[dict], date: str, s3_client, bucket_name: str, layer: str) -> None:
    """
    Save data as JSON to Cloudflare R2.

    Args:
        data: List of job dicts to save
        date: Date string for the filename (YYYY-MM-DD)
        s3_client: boto3 S3 client configured for R2
        bucket_name: R2 bucket name
        layer: Storage layer (bronze or silver)
    """
    key = f"{layer}/{date}.json"

    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(data, indent=2),
        )
        logger.info(f"Saved {len(data)} records to R2: {key}")
    except Exception as e:
        logger.error(f"Failed to save to R2: {e}")
        raise