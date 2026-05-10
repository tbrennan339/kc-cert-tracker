import re
import logging

logger = logging.getLogger(__name__)

CATEGORY_PATTERNS = {
    "Help Desk & Desktop Support": r'help\s*desk|desktop\s+(support|engineer|technician)|technical\s+support|it\s+support|it\s+specialist|it\s+technician|service\s+desk|intune|endpoint\s+(engineer|administrator|manager)',
    "Systems Administration": r'system[s]?\s+administrator|systems?\s+engineer|it\s+administrator|exchange\s+administrator|m365\s+administrator|microsoft\s+365\s+administrator',
    "Networking": r'network\s+(engineer|administrator|architect|design|security)',
    "Security": r'security\s+(analyst|engineer|architect|administrator|operations)|soc\s+analyst|cybersecurity|information\s+security|devsecops|penetration\s+tester|vulnerability\s+analyst|threat\s+analyst|incident\s+response|iam\s+engineer|identity\s+engineer',
    "Cloud": r'cloud\s+(engineer|architect|administrator|security)|iam\s+engineer|identity\s+engineer',
    "DevOps & SRE": r'devops|site\s+reliability|release\s+engineer|platform\s+engineer|sre\b',
}


def categorize_jobs(jobs: list[dict]) -> list[dict]:
    """
    Assign a job category based on title matching.

    Args:
        jobs: List of job dicts from silver layer

    Returns:
        Same list with 'job_category' field added to each job
    """
    for job in jobs:
        title = job.get("job_title", "")
        categories = []

        for cat_name, pattern in CATEGORY_PATTERNS.items():
            if re.search(pattern, title, re.IGNORECASE):
                categories.append(cat_name)

        job["job_category"] = categories if categories else ["Uncategorized"]

        if not categories:
            logger.warning(f"Uncategorized job: '{job.get('job_title')}' from '{job.get('company')}'")

    return jobs