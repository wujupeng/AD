import httpx
import json

base = "https://******/api"

with httpx.Client(verify=False) as c:
    r = c.post(f"{base}/auth/login", json={"username": "zhangwei", "password": "*****"})
    d = r.json()
    token = d.get("data", {}).get("access_token") or d.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Try creating offboarding request
    payload = {
        "ad_account": "liangyinlong",
        "offboarding_date": "2026-06-26T00:00:00",
        "mailbox_retention_days": 0,
        "mailbox_forward_to": "",
        "wipe_devices": True,
        "revoke_all_access": True,
    }
    r2 = c.post(f"{base}/v1/enterprise/identity/offboarding", json=payload, headers=headers)
    print(f"Status: {r2.status_code}")
    print(json.dumps(r2.json(), indent=2)[:800])