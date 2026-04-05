import hashlib
import re
import logging
import psycopg2

logger = logging.getLogger(__name__)

def normalize(text:str) -> str:
    """
        Normalize text for consistent comparison across job board sources.

        Strips all non-alphanumeric characters, replacing them with spaces
        to preserve word boundaries. Lowercases and collapses whitespace.
        This ensures descriptions from LinkedIn and Indeed produce identical
        output despite different formatting (markdown, newlines, etc).

        Args:
            text: Raw job description text

        Returns:
            Cleaned, lowercase string with single-space word separation
        """
    text = re.sub(r'[^a-z0-9]', ' ', text.lower())
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def fingerprint(text: str) -> str:
    """
        Generate an MD5 hash of the role-specific content in a job description.

        Uses characters 500-1500 of the normalized text to avoid company
        boilerplate intros (first ~500 chars) and benefits/EEO footers.
        For short descriptions under 500 chars, hashes the full text.

        Args:
            text: Raw job description text

        Returns:
            32-character MD5 hex digest
        """
    norm = normalize(text)
    chunk = norm[500:1500] if len(norm) > 500 else norm
    return hashlib.md5(chunk.encode()).hexdigest()

def deduplicate_jobs(jobs: list[dict], connection_string: str) -> list[dict]:
    """
        Remove duplicate job postings using description fingerprinting.

        Compares each job's fingerprint against hashes stored in the seen_jobs
        table from the last 21 days. Jobs with unseen fingerprints are kept
        and recorded; duplicates are logged with details of the original match
        for manual spot-checking. Jobs with no description are passed through.

        Args:
            jobs: List of job dicts from the bronze layer
            connection_string: PostgreSQL connection string

        Returns:
            Filtered list of jobs with duplicates removed
        """
    conn = psycopg2.connect(connection_string)
    try:
        cur = conn.cursor()
        cur.execute("""SELECT description_hash, first_seen, job_title, company 
                       FROM seen_jobs 
                       WHERE first_seen >= CURRENT_DATE - INTERVAL '21 days'""")
        rows = cur.fetchall()
        hash_map = {row[0]: {"first_seen": row[1], "job_title": row[2], "company": row[3]} for row in rows}
        logger.info(f"Loaded {len(hash_map)} existing hashes")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to load to PostgreSQL: {e}")
        raise
    else:
        deduped_jobs = []
        for job in jobs:
            desc = job.get('description') or ''
            if not desc:
                deduped_jobs.append(job)
                continue
            job_hash = fingerprint(desc)
            if job_hash not in hash_map:
                deduped_jobs.append(job)
                hash_map[job_hash] = {"first_seen": job['date_posted'], "job_title": job['job_title'], "company": job['company']}
                cur.execute(
                    """INSERT INTO seen_jobs (description_hash, first_seen, job_title, company)
                       VALUES (%s, %s, %s, %s)""",
                    (job_hash, job['date_posted'], job['job_title'], job['company'])
                )
            else:
                original = hash_map[job_hash]
                logger.info(
                    f"Duplicate: '{job['job_title']}' from '{job['company']}' "
                    f"matches '{original['job_title']}' from '{original['company']}' "
                    f"first seen {original['first_seen']}"
                )
        conn.commit()
        logger.info(f"Deduplicated: {len(jobs)} -> {len(deduped_jobs)} jobs")
        return deduped_jobs
    finally:
        cur.close()
        conn.close()