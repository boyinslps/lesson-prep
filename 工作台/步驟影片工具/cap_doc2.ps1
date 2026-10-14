$ErrorActionPreference='Stop'
$sp=$PSScriptRoot; Set-Location $sp; [Environment]::CurrentDirectory=$sp
. .\cdp.ps1; Connect-Cdp 9333; Size 1280 640
$base='file:///'+$sp.Replace([string][char]92,'/')
$all=@{}
foreach($s in 'p0','p1','p2','p3','p4','p5','p6','p7','p8','v2a','v2b','v2c','v2d','v2e','v2f','v2g','v3a','v3b','v3c','v3d','v3e','v4a','v4b','v4c','v4d','v4e'){
  Cdp 'Page.navigate' @{url="$base/mockdoc2.html?s=$s"} | Out-Null; Start-Sleep -Milliseconds 900
  $all[$s] = Js 'window.RECTS'
  Shot "$sp\shots\doc2_$s.png"
}
($all | ConvertTo-Json) | Set-Content 'shots\doc2_rects.json' -Encoding utf8
