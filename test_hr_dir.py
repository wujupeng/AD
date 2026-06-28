import json, subprocess
r = subprocess.run(['curl', '-sk', 'http://127.0.0.1:8000/api/dfs/files?path=\\\\dcser1\\share\\HR&site_code=cii_factory'],
    capture_output=True, text=True, timeout=15)
d = json.loads(r.stdout)
print(json.dumps(d, indent=2, ensure_ascii=False))