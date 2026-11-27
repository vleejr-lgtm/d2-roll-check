# D2 Roll Check: serves this folder at https://localhost:8443 (needed for "Sign in with Bungie").
#
# First run asks for admin ONE time to:
#   1. create a self-signed certificate for "localhost" (valid 5 years, can't sign other certificates)
#   2. trust it on this PC so Chrome/Edge show no warning
#   3. bind it to port 8443 and allow your user to listen there
# After that it runs as you, no admin needed.
#
# Usage:      powershell -ExecutionPolicy Bypass -File .\start-server-https.ps1
# Uninstall:  powershell -ExecutionPolicy Bypass -File .\start-server-https.ps1 -Uninstall   (asks for admin)

param([int]$Port = 8443, [switch]$SetupOnly, [switch]$Uninstall)

$FriendlyName = 'D2 Roll Check localhost'
$AppId = '{6f1c3c34-6a1e-4a59-9f43-7c1b8e5d0d21}'

function Test-Admin {
    $p = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}
function Get-AppCert {
    Get-ChildItem Cert:\LocalMachine\My | Where-Object { $_.FriendlyName -eq $FriendlyName -and $_.NotAfter -gt (Get-Date) } | Select-Object -First 1
}
function Test-Setup {
    $cert = Get-AppCert
    if (-not $cert) { return $false }
    $binding = netsh http show sslcert ipport=0.0.0.0:$Port 2>$null | Out-String
    return $binding -match $cert.Thumbprint
}
function Invoke-Elevated([string]$extra) {
    $argList = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Port $Port $extra"
    $proc = Start-Process powershell -Verb RunAs -ArgumentList $argList -Wait -PassThru
    return $proc.ExitCode
}

if ($Uninstall) {
    if (-not (Test-Admin)) { Invoke-Elevated '-Uninstall' | Out-Null; return }
    netsh http delete sslcert ipport=0.0.0.0:$Port | Out-Null
    netsh http delete urlacl url=https://localhost:$Port/ | Out-Null
    Get-ChildItem Cert:\LocalMachine\My, Cert:\LocalMachine\Root | Where-Object { $_.FriendlyName -eq $FriendlyName } | Remove-Item
    Write-Host 'Removed the D2 Roll Check certificate and port binding.'
    return
}

if ($SetupOnly) {
    # runs elevated
    $cert = Get-AppCert
    if (-not $cert) {
        $cert = New-SelfSignedCertificate -DnsName 'localhost' -CertStoreLocation Cert:\LocalMachine\My `
            -FriendlyName $FriendlyName -NotAfter (Get-Date).AddYears(5) -KeyUsage DigitalSignature, KeyEncipherment
        $root = New-Object System.Security.Cryptography.X509Certificates.X509Store('Root', 'LocalMachine')
        $root.Open('ReadWrite'); $root.Add($cert); $root.Close()
    }
    netsh http delete sslcert ipport=0.0.0.0:$Port 2>$null | Out-Null
    netsh http add sslcert ipport=0.0.0.0:$Port certhash=$($cert.Thumbprint) appid=$AppId | Out-Null
    netsh http delete urlacl url=https://localhost:$Port/ 2>$null | Out-Null
    netsh http add urlacl url=https://localhost:$Port/ user="$env:USERDOMAIN\$env:USERNAME" | Out-Null
    exit 0
}

if (-not (Test-Setup)) {
    Write-Host 'One-time HTTPS setup: Windows will ask for admin permission...'
    if (Test-Admin) { powershell -NoProfile -ExecutionPolicy Bypass -File $PSCommandPath -Port $Port -SetupOnly } else { Invoke-Elevated '-SetupOnly' | Out-Null }
    if (-not (Test-Setup)) { Write-Host 'HTTPS setup did not finish. Run this script again and accept the admin prompt.' -ForegroundColor Red; return }
    Write-Host 'HTTPS setup done.'
}

$root = (Resolve-Path $PSScriptRoot).Path
$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add("https://localhost:$Port/index.html#home")
$listener.Start()
Write-Host "Serving $root at https://localhost:$Port/  (Ctrl+C to stop)"
Start-Process "https://localhost:$Port/index.html#home"

$types = @{ '.html' = 'text/html; charset=utf-8'; '.js' = 'application/javascript'; '.css' = 'text/css'; '.png' = 'image/png'; '.ico' = 'image/x-icon' }
try {
    while ($listener.IsListening) {
        $task = $listener.GetContextAsync()
        while (-not $task.AsyncWaitHandle.WaitOne(500)) { }
        $ctx = $task.Result
        $rel = [Uri]::UnescapeDataString($ctx.Request.Url.AbsolutePath.TrimStart('/'))
        if (-not $rel) { $rel = 'index.html' }
        $full = [IO.Path]::GetFullPath((Join-Path $root $rel))
        if ($full.StartsWith($root) -and (Test-Path $full -PathType Leaf)) {
            $bytes = [IO.File]::ReadAllBytes($full)
            $ext = [IO.Path]::GetExtension($full).ToLower()
            $ctx.Response.ContentType = if ($types.ContainsKey($ext)) { $types[$ext] } else { 'application/octet-stream' }
            $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
        } else {
            $ctx.Response.StatusCode = 404
        }
        $ctx.Response.Close()
    }
} finally {
    $listener.Stop()
}
