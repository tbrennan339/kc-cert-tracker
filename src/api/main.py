import pathlib
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import psycopg2
import os
from dotenv import load_dotenv

project_root = pathlib.Path(__file__).resolve().parents[2]
env_path = project_root / "infrastructure" / "docker" / ".env"
load_dotenv(env_path)
app = FastAPI()
templates = Jinja2Templates(directory=pathlib.Path(__file__).resolve().parent / "templates")

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(name="dashboard.html", request=request)

@app.get("/certs")
def get_certs():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
                    SELECT cert_name, job_count, date 
                    FROM cert_daily_counts
                    ORDER BY job_count DESC
                """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [
            {"cert_name": row[0], "job_count": row[1], "date": str(row[2])}
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))