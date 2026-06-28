import httpx
import json

base = "https://******/api"

with httpx.Client(verify=False) as c:
    r = c.post(f"{base}/auth/login", json={"username": "zhangwei", "password": "*****"})
    d = r.json()
    token = d.get("data", {}).get("access_token") or d.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "employee_name": "李鹏飞",
        "ad_account": "2030",
        "department": "gc",
        "title": "采购员",
        "start_date": "2026-06-28T00:00:00",
    }
    r2 = c.post(f"{base}/v1/enterprise/identity/onboarding", json=payload, headers=headers)
    print(f"Status: {r2.status_code}")
    print(json.dumps(r2.json(), indent=2)[:800])