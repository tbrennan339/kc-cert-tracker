from src.etl.extractors.theirstack import extract_jobs
from dotenv import load_dotenv
from pathlib import Path
import datetime
import json
import logging
import os

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

api_key = os.getenv("THEIRSTACK_API_KEY")

today = datetime.date.today()

if __name__ == "__main__":
    try:
        jobs = extract_jobs(api_key, 10)
        with open(bronze_layer / f"{today}.json", "w") as f:
            json.dump(jobs, f, indent=2)
        logger.info(f"Saved {len(jobs)} jobs to bronze/{today}.json")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise



