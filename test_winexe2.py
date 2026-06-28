import subprocess
import sys

DC_IP = '******'
DOMAIN = 'CII'
USER = 'Administrator'
PASS = '*****'

print("Test 1: winexe with proper args...")
cmd = ['winexe', '--interactive=0', '--ostype=2', '-U', f'{DOMAIN}/{USER}%{PASS}', f'//{DC_IP}', 'cmd /c echo hello_world']
try:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    print(f"RC: {r.returncode}")
    print(f"OUT: [{r.stdout.strip()}]")
    print(f"ERR: [{r.stderr.strip()[:200]}]")
except Exception as e:
    print(f"Exception: {e}")

print("\nTest 2: winexe with reinstall...")
cmd2 = ['winexe', '--reinstall', '--interactive=0', '-U', f'{DOMAIN}/{USER}%{PASS}', f'//{DC_IP}', 'cmd /c echo hello_world']
try:
    r2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=30)
    print(f"RC: {r2.returncode}")
    print(f"OUT: [{r2.stdout.strip()}]")
    print(f"ERR: [{r2.stderr.strip()[:200]}]")
except Exception as e:
    print(f"Exception: {e}")