import httpx
import json

base = "https://******/api"

with httpx.Client(verify=False) as c:
    r = c.post(f"{base}/auth/login", json={"username": "zhangwei", "password": "*****"})
    d = r.json()
    token = d.get("data", {}).get("access_token") or d.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create offboarding
    print("=== 1. Create offboarding ===")
    r1 = c.post(f"{base}/v1/enterprise/identity/offboarding", json={"ad_account": "testuser", "offboarding_date": "2026-07-01T00:00:00", "mailbox_retention_days": 0, "wipe_device": True, "revoke_all_access": True}, headers=headers)
    print(f"Status: {r1.status_code}")
    print(json.dumps(r1.json(), indent=2)[:300])

    # 2. Create onboarding
    print("\n=== 2. Create onboarding ===")
    r2 = c.post(f"{base}/v1/enterprise/identity/onboarding", json={"employee_name": "Test User", "sam_account_name": "testuser2", "department": "IT", "position": "Engineer", "site": "hq"}, headers=headers)
    print(f"Status: {r2.status_code}")
    print(json.dumps(r2.json(), indent=2)[:300])

    # 3. List offboarding
    print("\n=== 3. List offboarding ===")
    r3 = c.get(f"{base}/v1/enterprise/identity/offboarding?limit=10", headers=headers)
    print(f"Status: {r3.status_code}")
    d3 = r3.json().get("data", [])
    print(f"Count: {len(d3)}")
    for req in d3[:3]:
        print(f"  {req.get('ad_account','?')} | {req.get('status','?')}")

    # 4. List onboarding
    print("\n=== 4. List onboarding ===")
    r4 = c.get(f"{base}/v1/enterprise/identity/onboarding?limit=10", headers=headers)
    print(f"Status: {r4.status_code}")
    d4 = r4.json().get("data", [])
    print(f"Count: {len(d4)}")
    for req in d4[:3]:
        print(f"  {req.get('sam_account_name','?')} | {req.get('employee_name','?')} | {req.get('status','?')}")

    # 5. Lifecycle events
    print("\n=== 5. Lifecycle events ===")
    r5 = c.get(f"{base}/v1/enterprise/identity/lifecycle-events?limit=10", headers=headers)
    print(f"Status: {r5.status_code}")
    d5 = r5.json().get("data", [])
    print(f"Count: {len(d5)}")
    for e in d5[:5]:
        print(f"  {e.get('event_type','?')} | {e.get('ad_account','?')} | {e.get('trigger_source','?')} | systems={e.get('affected_systems',[])}")