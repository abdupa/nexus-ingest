import requests
import json

# The API endpoint on your Ubuntu machine
API_URL = "http://localhost:8000/ingest"

# A mock payload simulating a high-level requirement
payload = {
    "tenant_id": "client_alpha_001",
    "site_type": "real_estate",
    "urls": [
        "https://httpbin.org/headers", 
        "https://httpbin.org/ip"
    ]
}

print("🚀 Sending ingestion request to Nexus-Ingest...")

try:
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        print("✅ Success! Job Queued.")
        print(f"📦 Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Connection Error: {e}")