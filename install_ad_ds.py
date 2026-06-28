import subprocess
import sys

DC_IP = '******'
USER = 'administrator'
PASS = '*****'

def winexe_exec(cmd_str):
    cmd = ['winexe', '--ostype=2', '-U', f'{USER}%{PASS}', f'//{DC_IP}', f'cmd /c chcp 65001 >nul & {cmd_str}']
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return r.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"

print("=== Domain Status ===")
print(winexe_exec('wmic computersystem get domain,partofdomain /format:list'))

print("\n=== IP Config ===")
print(winexe_exec('ipconfig | findstr IPv4'))

print("\n=== DNS Servers ===")
print(winexe_exec('ipconfig /all | findstr "DNS Servers"'))

print("\n=== Install AD-Domain-Services ===")
print(winexe_exec('powershell -Command "Install-WindowsFeature AD-Domain-Services -IncludeManagementTools"'))

print("\n=== Check AD DS Install State ===")
print(winexe_exec('powershell -Command "Get-WindowsFeature AD-Domain-Services | Format-List Name,InstallState"'))