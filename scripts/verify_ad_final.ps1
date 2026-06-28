$ErrorActionPreference = 'Stop'
$logFile = 'C:\verify_ad_log.txt'

function Write-Log($msg) {
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "$ts - $msg" | Out-File -Append -FilePath $logFile -Encoding UTF8
}

Write-Log "=== Final AD Verification ==="

try {
    Write-Log "Checking ADWS service..."
    $adws = Get-Service -Name ADWS
    Write-Log "ADWS Status: $($adws.Status)"

    if ($adws.Status -ne 'Running') {
        Write-Log "Starting ADWS..."
        Start-Service -Name ADWS
        Start-Sleep -Seconds 10
        $adws = Get-Service -Name ADWS
        Write-Log "ADWS Status after start: $($adws.Status)"
    }

    Import-Module ActiveDirectory
    Write-Log "ActiveDirectory module loaded."

    $dc = Get-ADDomainController
    Write-Log "HostName: $($dc.HostName)"
    Write-Log "Domain: $($dc.Domain)"
    Write-Log "Site: $($dc.Site)"
    Write-Log "IsGlobalCatalog: $($dc.IsGlobalCatalog)"
    Write-Log "IsReadOnly: $($dc.IsReadOnly)"

    $domain = Get-ADDomain
    Write-Log "NetBIOS: $($domain.NetBIOSName)"
    Write-Log "Forest: $($domain.Forest)"
    Write-Log "PDCEmulator: $($domain.PDCEmulator)"

    $dcs = Get-ADDomainController -Filter *
    foreach ($d in $dcs) {
        Write-Log "DC: $($d.HostName) | Site: $($d.Site) | GC: $($d.IsGlobalCatalog) | IP: $($d.IPv4Address)"
    }

    $users = Get-ADUser -Filter * -Properties SamAccountName
    Write-Log "Total users: $($users.Count)"
    foreach ($u in $users) {
        Write-Log "  User: $($u.SamAccountName) ($($u.DistinguishedName))"
    }

    $groups = Get-ADGroup -Filter *
    Write-Log "Total groups: $($groups.Count)"

    $ous = Get-ADOrganizationalUnit -Filter *
    Write-Log "Total OUs: $($ous.Count)"

    Write-Log "=== Verification Complete ==="
}
catch {
    Write-Log "EXCEPTION: $_"
}