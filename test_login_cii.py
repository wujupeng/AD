import json, subprocess

r = subprocess.run([
    'curl', '-sk', '-X', 'POST',
    'http://127.0.0.1:8000/api/auth/login',
    '-H', 'Content-Type: application/json',
    '-d', json.dumps({"username": "9999", "password": "*****"})
], capture_output=True, text=True, timeout=15)
d = json.loads(r.stdout)
print(json.dumps(d, indent=2, ensure_ascii=False))