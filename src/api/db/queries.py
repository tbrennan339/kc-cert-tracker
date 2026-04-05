import logging

logger = logging.getLogger(__name__)

def get_certs_last_7_days(conn):
    try:
        cur = conn.cursor()
        cur.execute("""SELECT cert_name, SUM(job_count) AS job_count
                       FROM cert_daily_counts
                       WHERE date >= CURRENT_DATE - INTERVAL '7 days' 
                       GROUP BY cert_name 
                       ORDER BY job_count DESC""")
        rows = cur.fetchall()
        logger.info(f"Successfully fetched cert mentions for the last 7 days")
        return rows
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to load to PostgreSQL: {e}")
        raise
    finally:
        cur.close()

def get_certs_last_30_days(conn):
    try:
        cur = conn.cursor()
        cur.execute("""SELECT cert_name, SUM(job_count) AS job_count
                       FROM cert_daily_counts
                       WHERE date >= CURRENT_DATE - INTERVAL '30 days' 
                       GROUP BY cert_name 
                       ORDER BY job_count DESC""")
        rows = cur.fetchall()
        logger.info(f"Successfully fetched cert mentions for the last 30 days")
        return rows
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to load to PostgreSQL: {e}")
        raise
    finally:
        cur.close()

def get_cert_trends(conn):
    try:
        cur = conn.cursor()
        cur.execute("""SELECT date, cert_name, job_count
                       FROM cert_daily_counts 
                       ORDER BY date ASC, cert_name""")
        rows = cur.fetchall()
        logger.info(f"Successfully fetched all cert mentions.")
        return rows
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to load to PostgreSQL: {e}")
        raise
    finally:
        cur.close()
