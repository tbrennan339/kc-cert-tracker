import logging
import pandas as pd
import psycopg2

logger = logging.getLogger(__name__)

def aggregate_certs(jobs: list[dict]) -> pd.DataFrame:
    """
    Aggregate certification mentions from job descriptions.

    Args:
        jobs: List of job dicts from silver layer

    Returns:
        DataFrame with amount of certification mentions on specific date
    """
    if not jobs:
        logger.info("No jobs to aggregate")
        return pd.DataFrame(columns=["cert_name", "job_count", "date"])

    jobs_df = pd.DataFrame(jobs)
    cert_df = (
        jobs_df.explode('certs_found')
        .dropna(subset=['certs_found'])
        .groupby(['certs_found', 'date_posted'])
        .size()
        .reset_index(name="job_count")
        .rename(columns={"certs_found": "cert_name", "date_posted": "date"})
    )

    logger.info(f"Aggregated {len(cert_df)} cert counts from {len(jobs)} jobs")
    return cert_df

def load_to_postgres(cert_counts: pd.DataFrame, connection_string: str) -> None:
    conn = psycopg2.connect(connection_string)

    try:
        cur = conn.cursor()

        for _, row in cert_counts.iterrows():
            cur.execute(
                """INSERT INTO cert_daily_counts (cert_name, job_count, date)
                   VALUES (%s, %s, %s) ON CONFLICT (cert_name, date) DO NOTHING""",
                (row["cert_name"], row["job_count"], row["date"])
            )

        conn.commit()
        logger.info(f"Loaded {len(cert_counts)} cert counts to PostgreSQL")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to load to PostgreSQL: {e}")
        raise
    finally:
        cur.close()
        conn.close()