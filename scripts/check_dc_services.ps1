$ErrorActionPreference = 'Continue'
$logFile = 'C:\dc_services_log.txt'

function Write-Log($msg) {
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "$ts - $msg" | Out-File -Append -FilePath $logFile -Encoding UTF8
}

Write-Log "=== Checking DC Services and Ports ==="

Write-Log "Checking services..."
$services = @('NTDS','DNS','Kdc','Netlogon','w32time','ADWS','W3SVC')
foreach ($svc in $services) {
    $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($s) {
        Write-Log "  $svc : Status=$($s.Status), StartType=$($s.StartType)"
    } else {
        Write-Log "  $svc : NOT FOUND"
    }
}

Write-Log "Checking listening ports..."
$ports = @(389, 636, 88, 53, 3268, 3269, 445, 9389)
foreach ($port in $ports) {
    $listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($listener) {
        Write-Log "  Port $port : LISTENING (PID: $($listener.OwningProcess))"
    } else {
        Write-Log "  Port $port : NOT LISTENING"
    }
}

Write-Log "Checking event log for DCPromo errors..."
$events = Get-WinEvent -FilterHashtable @{LogName='Directory Services';Level=2,3;MaxEvents=5} -ErrorAction SilentlyContinue
if ($events) {
    foreach ($e in $events) {
        Write-Log "  Event $($e.Id): $($e.Message.Substring(0, [Math]::Min(200, $e.Message.Length)))"
    }
} else {
    Write-Log "  No recent DS error events found."
}

Write-Log "Checking dcdiag..."
dcdiag 2>&1 | Select-Object -First 30 | ForEach-Object { Write-Log "  dcdiag: $_" }

Write-Log "=== Check Complete ==="