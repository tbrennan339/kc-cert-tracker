import pathlib
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import psycopg2

from src.api.db.queries import get_certs_last_7_days, get_certs_last_30_days, get_cert_trends
from src.config import Config
import sentry_sdk

if Config.SENTRY_DSN:
    sentry_sdk.init(dsn=Config.SENTRY_DSN)
app = FastAPI(docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory=pathlib.Path(__file__).resolve().parent / "templates")

def get_connection():
    return psycopg2.connect(Config.DATABASE_URL)

@app.get("/health")
def health():
    return {"status": "ok"}
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(name="dashboard.html", request=request)

@app.get("/api/certs/7d")
def get_certs_7d():
    conn = get_connection()
    try:
        rows = get_certs_last_7_days(conn)
        return [{"cert_name": row[0], "job_count": row[1]} for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/certs/30d")
def get_certs_30d():
    conn = get_connection()
    try:
        rows = get_certs_last_30_days(conn)
        return [{"cert_name": row[0], "job_count": row[1]} for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/certs/trends")
def get_certs_trends_route():
    conn = get_connection()
    try:
        rows = get_cert_trends(conn)
        return [{"date": str(row[0]), "cert_name": row[1], "job_count": row[2]} for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/sentry-test")
def sentry_test():
    raise Exception("Testing Sentry integration!")