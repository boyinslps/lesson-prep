$ErrorActionPreference='Stop'
$sp=$PSScriptRoot; Set-Location $sp; [Environment]::CurrentDirectory=$sp
. .\cdp.ps1; Connect-Cdp 9333; Size 1280 640
function Nav($u,$w=5){ Cdp 'Page.navigate' @{url=$u} | Out-Null; Start-Sleep $w }
$q = '微波爐 輻射 日本 查核'
Nav ('https://www.google.com/search?hl=zh-TW&q=' + [Uri]::EscapeDataString($q))
Js 'JSON.stringify(Array.from(document.querySelectorAll("a h3")).slice(0,6).map(function(h){return h.innerText.slice(0,40)+" | "+h.closest("a").href.slice(0,60)}))'
Js 'window.scrollTo(0,500); true' | Out-Null; Start-Sleep 1
Shot "$sp\shots\sp_g_results_D.png"
Nav 'https://tfc-taiwan.org.tw/?p=109294' 5
Js 'location.href + " | " + document.title'
Js 'window.scrollTo(0,200); true' | Out-Null; Start-Sleep 1
Shot "$sp\shots\sp_tfc_D2.png"
