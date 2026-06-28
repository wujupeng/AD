$ErrorActionPreference = 'Stop'
$logFile = 'C:\verify_dc_log.txt'

function Write-Log($msg) {
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "$ts - $msg" | Out-File -Append -FilePath $logFile -Encoding UTF8
}

Write-Log "=== Verifying DC Status ==="

try {
    Import-Module ActiveDirectory
    Write-Log "ActiveDirectory module loaded."

    $dc = Get-ADDomainController
    Write-Log "HostName: $($dc.HostName)"
    Write-Log "Domain: $($dc.Domain)"
    Write-Log "Site: $($dc.Site)"
    Write-Log "IsGlobalCatalog: $($dc.IsGlobalCatalog)"
    Write-Log "IsReadOnly: $($dc.IsReadOnly)"
    Write-Log "OperatingSystem: $($dc.OperatingSystem)"

    $domain = Get-ADDomain
    Write-Log "Domain NetBIOS: $($domain.NetBIOSName)"
    Write-Log "Domain Forest: $($domain.Forest)"
    Write-Log "DomainMode: $($domain.DomainMode)"
    Write-Log "PDCEmulator: $($domain.PDCEmulator)"
    Write-Log "RIDMaster: $($domain.RIDRoleOwner)"
    Write-Log "InfrastructureMaster: $($domain.InfrastructureMaster)"

    Write-Log "Listing all DCs in domain..."
    $dcs = Get-ADDomainController -Filter * | Select-Object HostName,Site,IsGlobalCatalog,IPv4Address
    foreach ($d in $dcs) {
        Write-Log "  DC: $($d.HostName) | Site: $($d.Site) | GC: $($d.IsGlobalCatalog) | IP: $($d.IPv4Address)"
    }

    Write-Log "Checking AD services..."
    $services = @('NTDS','DNS','KDC','Netlogon','w32time')
    foreach ($svc in $services) {
        $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
        if ($s) {
            Write-Log "  $svc : Status=$($s.Status), StartType=$($s.StartType)"
        } else {
            Write-Log "  $svc : NOT FOUND"
        }
    }

    Write-Log "Checking listening ports..."
    $ports = @(389, 636, 88, 53, 3268, 3269, 445)
    foreach ($port in $ports) {
        $listener = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($listener) {
            Write-Log "  Port $port : LISTENING (PID: $($listener.OwningProcess))"
        } else {
            Write-Log "  Port $port : NOT LISTENING"
        }
    }

    Write-Log "Counting users..."
    $users = Get-ADUser -Filter * -Properties SamAccountName
    Write-Log "Total users: $($users.Count)"

    Write-Log "Counting groups..."
    $groups = Get-ADGroup -Filter *
    Write-Log "Total groups: $($groups.Count)"

    Write-Log "=== Verification Complete ==="
}
catch {
    Write-Log "EXCEPTION: $_"
}