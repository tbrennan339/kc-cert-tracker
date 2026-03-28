"""TheirStack job postings API extractor."""
import logging
import requests

logger = logging.getLogger(__name__)

# Config
THEIRSTACK_URL = "https://api.theirstack.com/v1/jobs/search"

# Kansas City metro area location IDs from TheirStack API
# Sourced from TheirStack GUI search for KC metro area
# Includes KC MO, KC KS, Overland Park, Olathe, Lenexa, Lee's Summit, etc.
KC_METRO_LOCATION_IDS = [
    {"id": 4271935},
    {"id": 4271942},
    {"id": 4273836},
    {"id": 4273837},
    {"id": 4274236},
    {"id": 4274305},
    {"id": 4274315},
    {"id": 4274317},
    {"id": 4274320},
    {"id": 4274356},
    {"id": 4274359},
    {"id": 4275393},
    {"id": 4275395},
    {"id": 4276614},
    {"id": 4276617},
    {"id": 4276618},
    {"id": 4276816},
    {"id": 4276826},
    {"id": 4276873},
    {"id": 4276875},
    {"id": 4277717},
    {"id": 4277718},
    {"id": 4277720},
    {"id": 4279247},
    {"id": 4279274},
    {"id": 4282094},
    {"id": 4376482},
    {"id": 4377664},
    {"id": 4387990},
    {"id": 4388402},
    {"id": 4388460},
    {"id": 4391812},
    {"id": 4393217},
    {"id": 4394870},
    {"id": 4395052},
    {"id": 4400860},
    {"id": 4405180},
    {"id": 4405185},
    {"id": 4405188},
    {"id": 4274239},
]

DEFAULT_JOB_TITLES = [
    "security analyst",
    "security engineer",
    "soc analyst",
    "cybersecurity analyst",
    "information security",
    "network engineer",
    "network administrator",
    "systems administrator",
    "infrastructure engineer",
    "help desk",
    "desktop support",
    "technical support",
    "IT support",
    "IT specialist",
    "desktop engineer",
    "cloud engineer",
    "devops engineer",
    "site reliability engineer",
    "IT administrator",
    "IT technician",
    "systems engineer",
    "system administrator",
]

DEFAULT_SOURCES = [
    "indeed.com",
    "linkedin.com",
    "ziprecruiter.com",
    "glassdoor.com",
]


def extract_jobs(api_key: str, limit: int = 25) -> list[dict]:
    """
    Pull job postings from TheirStack API.

    Args:
        api_key: TheirStack API key
        limit: Max number of jobs to return

    Returns:
        List of job dictionaries from the API

    Raises:
        requests.exceptions.HTTPError: If API returns an error status
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = {
        "page": 0,
        "limit": limit,
        "posted_at_max_age_days": 0,
        "blur_company_data": False,
        "include_total_results": False,
        "job_title_or": DEFAULT_JOB_TITLES,
        "job_location_or": KC_METRO_LOCATION_IDS,
        "url_domain_or": DEFAULT_SOURCES,
    }

    try:
        response = requests.post(
            THEIRSTACK_URL, json=body, headers=headers, timeout=30
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"TheirStack API error: {e}")
        raise
    except requests.exceptions.ConnectionError:
        logger.error("Could not connect to TheirStack API")
        raise
    except requests.exceptions.Timeout:
        logger.error("TheirStack API request timed out")
        raise

    data = response.json()
    jobs = data.get("data", [])
    logger.info(f"Extracted {len(jobs)} jobs from TheirStack")
    return jobs
