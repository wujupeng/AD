import httpx
import json

base = "https://******/api"

with httpx.Client(verify=False) as c:
    r = c.post(f"{base}/auth/login", json={"username": "zhangwei", "password": "*****"})
    d = r.json()
    token = d.get("data", {}).get("access_token") or d.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List onboarding
    print("=== 1. Onboarding list ===")
    r1 = c.get(f"{base}/v1/enterprise/identity/onboarding?limit=10", headers=headers)
    d1 = r1.json().get("data", [])
    for req in d1:
        print(f"  {req['sam_account_name']} | {req['employee_name']} | status={req['status']} | step_results={req.get('step_results',{})}")

    # 2. Execute onboarding for 2030 (find its request_id)
    for req in d1:
        if req['sam_account_name'] == '2030':
            print(f"\n=== 2. Execute onboarding for 2030 (id={req['request_id'][:8]}...) ===")
            r2 = c.post(f"{base}/v1/enterprise/identity/onboarding/{req['request_id']}/execute", headers=headers)
            print(f"Status: {r2.status_code}")
            print(json.dumps(r2.json(), indent=2)[:400])
            break

    # 3. Check lifecycle events
    print("\n=== 3. Lifecycle events ===")
    r3 = c.get(f"{base}/v1/enterprise/identity/lifecycle-events?limit=20", headers=headers)
    d3 = r3.json().get("data", [])
    onboarding = [e for e in d3 if e.get("event_type","").startswith("onboarding")]
    offboarding = [e for e in d3 if e.get("event_type","").startswith("offboarding")]
    print(f"Onboarding: {len(onboarding)}, Offboarding: {len(offboarding)}")