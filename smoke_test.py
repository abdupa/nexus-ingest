import os
import requests
from core.stealth import StealthEngine

def run_smoke_test():
    print("🚀 Starting Nexus Ingest Smoke Test...")
    stealth = StealthEngine()
    
    # Test 1: Local IP Check
    print("\n[1/3] Checking Local IP...")
    local_res = requests.get("https://api.ipify.org?format=json")
    print(f"📍 Local IP: {local_res.json().get('ip')}")

    # Test 2: Proxy Tiering Check (Datacenter)
    print("\n[2/3] Checking Datacenter Proxy (US)...")
    dc_res = stealth.get("https://api.ipify.org?format=json", tier="datacenter")
    if dc_res:
        print(f"🛡️ Proxy IP: {dc_res.json().get('ip')}")
    else:
        print("⚠️ Datacenter Proxy failed or not configured.")

    # Test 3: Stealth Engine & Target Reachability (Amazon)
    print("\n[3/3] Checking Amazon US Reachability...")
    amz_res = stealth.get("https://www.amazon.com/dp/B0D9M3K7K7", tier="datacenter")
    if amz_res and amz_res.status_code == 200:
        print("✅ Amazon US reached successfully via StealthEngine!")
    else:
        print(f"❌ Amazon US Blocked (Status: {amz_res.status_code if amz_res else 'No Response'})")

if __name__ == "__main__":
    run_smoke_test()