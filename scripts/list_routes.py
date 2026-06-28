import httpx
r = httpx.Client(verify=False).get("https://******/api/openapi.json")
if r.status_code == 200:
    paths = sorted(r.json().get("paths", {}).keys())
    for p in paths:
        print(p)