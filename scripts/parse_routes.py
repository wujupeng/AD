import json
d = json.load(open("/tmp/openapi.json"))
for p in sorted(d.get("paths", {}).keys()):
    print(p)
