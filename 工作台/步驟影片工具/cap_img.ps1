$ErrorActionPreference='Stop'
$sp=$PSScriptRoot; Set-Location $sp; [Environment]::CurrentDirectory=$sp
. .\cdp.ps1; Connect-Cdp 9333; Size 1280 640
$base='file:///'+$sp.Replace([string][char]92,'/')
foreach($s in 'base','menu'){
  Cdp 'Page.navigate' @{url="$base/mock_copyimg.html?s=$s"} | Out-Null; Start-Sleep -Milliseconds 1200
  if($s -eq 'menu'){ Set-Content 'shots\img_copy_rects.json' (Js 'window.RECTS') -Encoding utf8 }
  Shot "$sp\shots\img_copy_$s.png"
}
