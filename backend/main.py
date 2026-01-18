import os, uuid, logging, time
from typing import List
from fastapi import FastAPI, Response
from pydantic import BaseModel, HttpUrl
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from celery import Celery

# --- INTERNAL IMPORTS ---
from database import engine  # Single source of truth for the DB engine
from core.models import Base # Needed for the Magic Command
from tasks import process_scrape_task

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus.api")

# --- DATABASE INITIALIZATION ---
# Create tables if they don't exist immediately on startup
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables verified/created.")
except Exception as e:
    logger.error(f"❌ Database initialization failed: {e}")

# --- CELERY SETUP ---
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
celery_app = Celery("nexus_tasks", broker=CELERY_BROKER_URL)

app = FastAPI(title="Nexus-Ingest Factory")

# --- ENDPOINTS ---
@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health():
    return {"status": "online", "machine": "nexus-ingest-factory"}

class ScrapeRequest(BaseModel):
    tenant_id: str
    site_type: str 
    urls: List[HttpUrl]

@app.post("/ingest")
async def start_job(request: ScrapeRequest):
    job_id = str(uuid.uuid4())
    logger.info(f"🚀 INGEST START | Job: {job_id} | URLs: {len(request.urls)}")
    
    try:
        for url in request.urls:
            # Dispatch to worker via name string to decouple API from worker logic
            result = celery_app.send_task(
                "process_scrape_task",
                args=[str(url), request.site_type, request.tenant_id, job_id]
            )
            logger.info(f"  ✔ Queued: {url} | Task ID: {result.id}")
            
        return {"job_id": job_id, "status": "queued"}

    except Exception as e:
        logger.error(f"  ❌ DISPATCH FAILED: {str(e)}", exc_info=True)
        return {"status": "error", "message": "Broker unreachable"}