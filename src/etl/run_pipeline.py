from src.etl.extractors.theirstack import extract_jobs
from dotenv import load_dotenv
from pathlib import Path
import datetime
import json
import logging
import os

from src.etl.loaders.gold import aggregate_certs, load_to_postgres
from src.etl.transformers.cert_extractor import extract_certs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

project_root = Path(__file__).resolve().parents[2]
env_path = project_root / "infrastructure" / "docker" / ".env"
load_dotenv(env_path)

bronze_layer = project_root / "data" / "bronze"
bronze_layer.mkdir(parents=True, exist_ok=True)

silver_layer = project_root / "data" / "silver"
silver_layer.mkdir(parents=True, exist_ok=True)

api_key = os.getenv("THEIRSTACK_API_KEY")
connection_string = os.getenv("DATABASE_URL")

today = datetime.date.today()

if __name__ == "__main__":
    try:
        # Extract
        jobs = extract_jobs(api_key, 10)
        with open(bronze_layer / f"{today}.json", "w") as f:
            json.dump(jobs, f, indent=2)
        logger.info(f"Saved {len(jobs)} jobs to bronze/{today}.json")

        # Transform
        jobs_with_certs = extract_certs(jobs)
        with open(silver_layer / f"{today}.json", "w") as f:
            json.dump(jobs_with_certs, f, indent=2)
        logger.info(f"Saved {len(jobs_with_certs)} jobs to silver/{today}.json")

        # Load
        aggregate_data = aggregate_certs(jobs_with_certs)
        load_to_postgres(aggregate_data, connection_string)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


