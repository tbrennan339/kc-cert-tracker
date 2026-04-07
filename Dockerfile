FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir requests boto3 psycopg2-binary pandas python-dotenv fastapi uvicorn jinja2

COPY src/ src/

EXPOSE 8080

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8080"]