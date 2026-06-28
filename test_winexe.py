import subprocess
import sys

DC_IP = '******'
DOMAIN = 'CII'
USER = 'Administrator'
PASS = '*****'

print("Testing winexe...")
cmd = ['winexe', f'-U', f'{DOMAIN}/{USER}%{PASS}', f'//{DC_IP}', 'cmd /c echo test123']
print(f"Command: {' '.join(cmd)}")
try:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    print(f"Return code: {r.returncode}")
    print(f"Stdout: [{r.stdout}]")
    print(f"Stderr: [{r.stderr}]")
except Exception as e:
    print(f"Exception: {e}")

print("\nTrying with --system flag...")
cmd2 = ['winexe', '--system', '-U', f'{DOMAIN}/{USER}%{PASS}', f'//{DC_IP}', 'cmd /c whoami']
try:
    r2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=20)
    print(f"Return code: {r2.returncode}")
    print(f"Stdout: [{r2.stdout}]")
    print(f"Stderr: [{r2.stderr}]")
except Exception as e:
    print(f"Exception: {e}")