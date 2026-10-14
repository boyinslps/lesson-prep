$sp=$PSScriptRoot; Set-Location $sp; [Environment]::CurrentDirectory=$sp
. .\cdp.ps1; Connect-Cdp 9333; Size 760 520
$base='file:///'+$sp.Replace([string][char]92,'/')
Cdp 'Page.navigate' @{url="$base/mock_line.html"} | Out-Null; Start-Sleep 2
Shot "$sp\shots\line_c.png"
