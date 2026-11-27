# Serves this folder at http://localhost:8000 so the Bungie API accepts requests from the page.
# Usage:  powershell -ExecutionPolicy Bypass -File .\start-server.ps1   (Ctrl+C to stop)
param([int]$Port = 8000)

$root = (Resolve-Path $PSScriptRoot).Path
$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add("http://localhost:$Port/")
$listener.Start()
Write-Host "Serving $root at http://localhost:$Port/  (Ctrl+C to stop)"
Start-Process "http://localhost:$Port/"

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
