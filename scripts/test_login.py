import httpx
import json

base = "https://******/api"

with httpx.Client(verify=False) as c:
    # Test Administrator login
    r = c.post(f"{base}/auth/login", json={"username": "Administrator", "password": "*****"})
    print(f"Administrator login: {r.status_code}")
    d = r.json()
    print(json.dumps(d, indent=2)[:300])
    
    # Test 1000 user
    r2 = c.post(f"{base}/auth/login", json={"username": "1000", "password": "*****"})
    print(f"\n1000 login: {r2.status_code}")
    d2 = r2.json()
    print(json.dumps(d2, indent=2)[:300])