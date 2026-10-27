$ErrorActionPreference='Stop'
$sp=$PSScriptRoot; Set-Location $sp; [Environment]::CurrentDirectory=$sp
. .\cdp.ps1; Connect-Cdp 9333; Size 1280 640
$q = '手機充電 講電話 喝水 查核'
$u = 'https://www.google.com/search?hl=zh-TW&q=' + [Uri]::EscapeDataString($q)
Cdp 'Page.navigate' @{url=$u} | Out-Null; Start-Sleep 5
Js 'window.scrollTo(0,640); true' | Out-Null; Start-Sleep 1
$t = Js 'JSON.stringify(Array.from(document.querySelectorAll("a h3")).slice(0,6).map(function(h){var a=h.closest("a");var c=a.getBoundingClientRect();var s=a.closest("div[data-hveid]")||a;var d=s.getBoundingClientRect();return {t:h.innerText.slice(0,30),x:Math.round(c.left),y:Math.round(c.top),w:Math.round(c.width),h:Math.round(c.height),dy:Math.round(d.top),dh:Math.round(d.height)}}))'
Set-Content 'shots\sp_g_results2.json' $t -Encoding utf8
Shot "$sp\shots\sp_g_results2.png"
