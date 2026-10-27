$ErrorActionPreference='Stop'
$sp=$PSScriptRoot; Set-Location $sp; [Environment]::CurrentDirectory=$sp
. .\cdp.ps1; Connect-Cdp 9333; Size 1280 640
$base='file:///'+$sp.Replace([string][char]92,'/')
$all=@{}
foreach($s in 'a0','a1','a2','a3','a4','a5','a6','b0','b1','b2','b3','b4','c0','c1','c2','c3','c4','c5','c6','d0','d1','d2','d3','d4'){
  Cdp 'Page.navigate' @{url="$base/mockdoc4.html?s=$s"} | Out-Null; Start-Sleep -Milliseconds 900
  $all[$s] = Js 'window.RECTS'
  Shot "$sp\shots\doc4_$s.png"
}
($all | ConvertTo-Json) | Set-Content 'shots\doc4_rects.json' -Encoding utf8
"done"
