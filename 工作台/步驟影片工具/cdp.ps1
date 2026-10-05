# Minimal Chrome DevTools Protocol client (Windows PowerShell 5.1)
# Usage: . .\cdp.ps1 ; Connect-Cdp 9333 ; Cdp 'Page.navigate' @{url='...'} ; Shot 'out.png'
$ErrorActionPreference = 'Stop'
$script:ws = $null; $script:id = 0

function Connect-Cdp([int]$port) {
  $tabs = Invoke-RestMethod "http://127.0.0.1:$port/json"
  $page = $tabs | Where-Object { $_.type -eq 'page' } | Select-Object -First 1
  $script:ws = New-Object System.Net.WebSockets.ClientWebSocket
  $script:ws.Options.KeepAliveInterval = [TimeSpan]::FromSeconds(20)
  $script:ws.ConnectAsync([Uri]$page.webSocketDebuggerUrl, [Threading.CancellationToken]::None).Wait()
}

function Recv-Msg {
  $buf = New-Object byte[] 1048576
  $ms = New-Object System.IO.MemoryStream
  do {
    $seg = New-Object System.ArraySegment[byte] -ArgumentList (, $buf)
    $r = $script:ws.ReceiveAsync($seg, [Threading.CancellationToken]::None).Result
    $ms.Write($buf, 0, $r.Count)
  } while (-not $r.EndOfMessage)
  return [Text.Encoding]::UTF8.GetString($ms.ToArray())
}

function Cdp([string]$method, $params = @{}) {
  $script:id++
  $myId = $script:id
  $msg = @{ id = $myId; method = $method; params = $params } | ConvertTo-Json -Depth 20 -Compress
  $bytes = [Text.Encoding]::UTF8.GetBytes($msg)
  $seg = New-Object System.ArraySegment[byte] -ArgumentList (, $bytes)
  $script:ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [Threading.CancellationToken]::None).Wait()
  while ($true) {
    $txt = Recv-Msg
    if ($txt -match ('^\{"id":' + $myId + ',')) { return ($txt | ConvertFrom-Json) }
  }
}

function Js([string]$expr) {
  $r = Cdp 'Runtime.evaluate' @{ expression = $expr; returnByValue = $true; awaitPromise = $true }
  if ($r.result.exceptionDetails) { throw ("JS error: " + ($r.result.exceptionDetails | ConvertTo-Json -Depth 6 -Compress)) }
  return $r.result.result.value
}

function Shot([string]$path) {
  $r = Cdp 'Page.captureScreenshot' @{ format = 'png'; fromSurface = $true }
  [IO.File]::WriteAllBytes($path, [Convert]::FromBase64String($r.result.data))
}

function Size([int]$w, [int]$h) {
  Cdp 'Emulation.setDeviceMetricsOverride' @{ width = $w; height = $h; deviceScaleFactor = 1; mobile = $false } | Out-Null
}
