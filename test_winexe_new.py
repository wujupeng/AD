import subprocess
import sys

DC_IP = '******'
USER = 'administrator'
PASS = '*****'

print("Test 1: winexe to ******...")
cmd = ['winexe', '-U', f'{USER}%{PASS}', f'//{DC_IP}', 'cmd /c echo hello']
try:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    print(f"RC: {r.returncode}")
    print(f"OUT: [{r.stdout.strip()}]")
    print(f"ERR: [{r.stderr.strip()[:200]}]")
except Exception as e:
    print(f"Exception: {e}")

print("\nTest 2: winexe with --ostype=2...")
cmd2 = ['winexe', '--ostype=2', '-U', f'{USER}%{PASS}', f'//{DC_IP}', 'cmd /c hostname']
try:
    r2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=20)
    print(f"RC: {r2.returncode}")
    print(f"OUT: [{r2.stdout.strip()}]")
    print(f"ERR: [{r2.stderr.strip()[:200]}]")
except Exception as e:
    print(f"Exception: {e}")