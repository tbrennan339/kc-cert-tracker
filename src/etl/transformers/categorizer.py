import re
import logging

logger = logging.getLogger(__name__)

CATEGORY_PATTERNS = {
    "Help Desk & Desktop Support": r'help\s*desk|desktop\s+(support|engineer|technician)|technical\s+(support|customer)|it\s+support|it\s+specialist|it\s+technician|service\s+desk|intune|endpoint\s+(engineer|administrator|manager)|it\s+operations\s+specialist|it\s+field|field\s+support\s+technician|pc\s+support|it\s+service\s+desk|it\s+onboarding|it\s+applications?\s+specialist|it\s+prod\s+support|it\s+systems.*support|vip\s+.*support|it\s+manufacturing.*technician|lead\s+it\s+product\s+support|sr\s+it\s+exec',
    "Systems Administration": r'system[s]?\s+administrator|systems?\s+engineer|it\s+administrator|exchange\s+administrator|m365\s+administrator|microsoft\s+365\s+administrator|it\s+operations\s+administrator|database\s+administrator|server\s+administrator|it\s+systems.*administrator|it\s+systems\s+integration|it\s+network.*systems\s+specialist|lead\s+it\s+systems|learning\s+management\s+system.*administrator',
    "Networking": r'network\s+(engineer|administrator|architect|design|security|implementation|automation|equipment)|it\s+network.*telecom',
    "Security": r'security\s+(analyst|engineer|architect|administrator|operations|officer|software)|soc\s+analyst|cybersecurity|information\s+security|devsecops|penetration\s+tester|vulnerability\s+analyst|threat\s+analyst|incident\s+response|security\s+linux|information\s+systems\s+security|isso\b|information\s+technology\s+security|security\s+idaas|security\s+systems\s+analyst|security\s+alignment|security\s+project',
    "Cloud": r'cloud\s+(engineer|architect|administrator|security|data|testing)|iam\s+engineer|identity\s+engineer|azure\s+cloud|infrastructure\s+engineer|test\s+engineer.*cloud',
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