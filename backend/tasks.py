import logging
import os
import sys
import random
import time
import redis
from datetime import datetime

# Pathing for Docker/Microservice Package Resolution
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from celery import Celery
from celery.utils.log import get_task_logger
from prometheus_client import CollectorRegistry, Counter, push_to_gateway

# Core & Strategies
from core.stealth import stealth_engine 
from database import SessionLocal           
from core.models import ScrapedRecord
from strategies import get_strategy_for_url

# --- 🟢 PROMETHEUS CONFIGURATION (The "Senior" Way) ---
# We use a persistent registry to hold our metrics between pushes
nexus_registry = CollectorRegistry()
SCRAPE_SUCCESS = Counter(
    'nexus_success_total', 
    'Total successful scrapes', 
    ['site_type'], 
    registry=nexus_registry
)
SCRAPE_FAILURE = Counter(
    'nexus_failure_total', 
    'Failed Scrapes', 
    ['site_type', 'error_type'], 
    registry=nexus_registry
)

# Worker Initialization
worker_app = Celery('nexus_tasks', broker=os.getenv('CELERY_BROKER_URL'))
logger = get_task_logger(__name__)
r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

@worker_app.task(name="process_scrape_task", bind=True)
def process_scrape_task(self, url, site_type, tenant_id, job_id):
    # --- 1. DEDUPLICATION GATEKEEPER ---
    dedup_key = f"cache:success:{site_type}"
    if r.sismember(dedup_key, url) or r.sismember(f"seen_urls:{tenant_id}", url):
        logger.info(f"⏭️ Skipping: {url} (Already in cache)")
        return {"status": "skipped", "url": url}

    # --- 2. CIRCUIT BREAKER ---
    if r.get(f"circuit_breaker:{site_type}"):
        logger.warning(f"🚨 Circuit Open for {site_type}. Postponing...")
        raise self.retry(countdown=300, max_retries=100) 

    # --- 3. PROXY TIERING ---
    current_attempt = self.request.retries
    proxy_tier = "residential" if current_attempt > 0 else "datacenter"
    
    try:
        strategy = get_strategy_for_url(url, stealth_engine)
        raw_data = strategy.execute_fetch(url, tier=proxy_tier, mimic_human=True)

        if not raw_data or raw_data.get("price") == "0":
            fails = r.incr(f"fail_count:{site_type}")
            if fails > 5:
                r.setex(f"circuit_breaker:{site_type}", 600, "active") 
            raise ValueError("Zero-Price/Blocked detection")

        # --- 4. DB PERSISTENCE ---
        with SessionLocal() as db:
            new_record = ScrapedRecord(
                tenant_id=tenant_id,
                project_id="gadgetph_tracking",
                source_url=url,
                payload=raw_data,
                success=True,
                timestamp=datetime.utcnow()
            )
            db.add(new_record)
            db.commit()
            logger.info(f"💾 DATABASE PERSISTED: {url}")

        # --- 5. REDIS SUCCESS STATE ---
        with r.pipeline() as pipe:
            pipe.delete(f"fail_count:{site_type}")
            pipe.sadd(dedup_key, url)
            pipe.sadd(f"seen_urls:{tenant_id}", url)
            pipe.expire(dedup_key, 86400) 
            pipe.execute()

        # --- 📈 MONITORING SUCCESS PUSH ---
        # --- Updated Monitoring Success Push ---
        SCRAPE_SUCCESS.labels(site_type=site_type).inc()
        try:
            # Use the hostname to identify the specific container
            import socket
            instance_name = socket.gethostname() 
            
            push_to_gateway(
                'pushgateway:9091', 
                job='nexus_worker', 
                registry=nexus_registry,
                grouping_key={'instance': instance_name} # THIS IS THE FIX
            )
        except Exception as e:
            logger.warning(f"📈 Metrics Push Failed: {e}")

        logger.info(f"✅ SUCCESS: {url} | Tier: {proxy_tier}")
        return {"status": "ok", "url": url}

    except Exception as e:
        # --- 📈 MONITORING FAILURE PUSH ---
        SCRAPE_FAILURE.labels(site_type=site_type, error_type=type(e).__name__).inc()
        try:
            push_to_gateway('pushgateway:9091', job='nexus_worker', registry=nexus_registry)
        except Exception as em:
            logger.warning(f"📈 Metrics failure push failed: {em}")

        # Human-like Jitter Backoff
        base_wait = (2 ** current_attempt) * 30 
        final_wait = int(base_wait * random.uniform(0.8, 1.2))
        
        logger.error(f"💥 Attempt {current_attempt} failed: {str(e)}")
        raise self.retry(exc=e, countdown=final_wait, max_retries=3)