import httpx
import json

base = "https://******/api"

with httpx.Client(verify=False) as c:
    r = c.post(f"{base}/auth/login", json={"username": "zhangwei", "password": "*****"})
    d = r.json()
    token = d.get("data", {}).get("access_token") or d.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Lifecycle events
    print("=== 1. Lifecycle events ===")
    r1 = c.get(f"{base}/v1/enterprise/identity/lifecycle-events?limit=50", headers=headers)
    print(f"Status: {r1.status_code}")
    print(json.dumps(r1.json(), indent=2)[:500])

    # 2. Lifecycle by account
    print("\n=== 2. Lifecycle by account (liangyinlong) ===")
    r2 = c.get(f"{base}/v1/enterprise/identity/lifecycle/liangyinlong", headers=headers)
    print(f"Status: {r2.status_code}")
    print(json.dumps(r2.json(), indent=2)[:500])

    # 3. Offboarding list
    print("\n=== 3. Offboarding list ===")
    r3 = c.get(f"{base}/v1/enterprise/identity/offboarding?limit=10", headers=headers)
    print(f"Status: {r3.status_code}")
    d3 = r3.json().get("data", [])
    print(f"Count: {len(d3)}")
    for req in d3:
        print(f"  {req.get('ad_account','?')} | {req.get('status','?')} | {req.get('offboarding_date','?')}")

    # 4. Onboarding list
    print("\n=== 4. Onboarding list ===")
    r4 = c.get(f"{base}/v1/enterprise/identity/onboarding?limit=10", headers=headers)
    print(f"Status: {r4.status_code}")
    d4 = r4.json().get("data", [])
    print(f"Count: {len(d4)}")
    for req in d4:
        print(f"  {req.get('sam_account_name','?')} | {req.get('employee_name','?')} | {req.get('status','?')}")