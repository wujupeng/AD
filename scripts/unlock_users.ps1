$ErrorActionPreference = 'Continue'
$logFile = 'C:\unlock_users_log.txt'

function Write-Log($msg) {
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "$ts - $msg" | Out-File -Append -FilePath $logFile -Encoding UTF8
}

Write-Log "=== Unlocking AD User Accounts ==="

try {
    Import-Module ActiveDirectory

    $lockedUsers = Search-ADAccount -LockedOut
    Write-Log "Locked users count: $($lockedUsers.Count)"
    foreach ($u in $lockedUsers) {
        Write-Log "  Locked: $($u.SamAccountName) ($($u.DistinguishedName))"
        Unlock-ADAccount -Identity $u.SamAccountName
        Write-Log "  Unlocked: $($u.SamAccountName)"
    }

    if ($lockedUsers.Count -eq 0) {
        Write-Log "No locked users found. Trying specific user 9999..."
        try {
            Unlock-ADAccount -Identity '9999'
            Write-Log "Unlocked 9999"
        } catch {
            Write-Log "Could not unlock 9999 via AD module: $_"
        }
    }

    Write-Log "=== Unlock Complete ==="
}
catch {
    Write-Log "AD Module failed, trying net user command..."
    net user 9999 /domain /active:yes 2>&1 | ForEach-Object { Write-Log "  net user: $_" }
    Write-Log "=== Unlock Complete (fallback) ==="
}