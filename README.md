# Nexus Ingest: Universal Stealth Ingestion Engine 🚀

A high-performance, multi-tenant web ingestion backend built for scale. Designed to bypass enterprise-grade anti-bot protections while maintaining strict cost-efficiency (Unit Economics).



## 🏗️ Architectural Highlights
- **Universal Strategy Pattern**: Auto-discovery logic for multi-platform support (Shopee, Amazon, etc.).
- **Stealth Engine**: JA3/TLS Fingerprinting via `curl_cffi` to mimic high-fidelity browser profiles (iOS/Chrome/Safari).
- **Expert Hardening**: 
    - **Circuit Breaker**: Redis-backed logic to pause ingestion on high-failure rates (protects IP reputation and saves proxy costs).
    - **Exponential Jitter**: Randomized human-like pacing to bypass behavioral analysis.
    - **Proxy Tiering**: Automatic escalation from Datacenter to Residential IPs only when detection is triggered.
- **Universal Schema**: PostgreSQL with **JSONB** support for schema-less data payloads.



## 🧩 System Flow
1. **API Layer**: FastAPI ingestion gateway.
2. **Task Queue**: Celery distributed workers running on Ubuntu.
3. **Strategy Factory**: Dynamic domain detection and extraction routing.
4. **Persistence**: Validated persistence to a centralized Universal DB.

## 🛠️ Tech Stack
- **Backend**: Python 3.11 (FastAPI, Celery)
- **Data**: Redis, PostgreSQL 15
- **Infrastructure**: Docker & Docker-Compose
- **Stealth**: curl_cffi, Custom Headers, Jitter Pacing

---
*Developed by ABDupa | Specialized in Scalable Data Pipelines and Anti-Bot Bypass Strategies.*
