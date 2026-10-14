$sp=$PSScriptRoot; Set-Location $sp; [Environment]::CurrentDirectory=$sp
. .\cdp.ps1; Connect-Cdp 9333; Size 1280 640
Cdp 'Page.navigate' @{url='https://www.mygopen.com/2026/02/ai-fraud.html'} | Out-Null; Start-Sleep 5
Js 'window.scrollTo(0,150); true' | Out-Null; Start-Sleep 1
Shot "$sp\shots\v1_mgp2.png"
