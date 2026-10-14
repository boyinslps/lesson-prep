$ErrorActionPreference='Stop'
$sp=$PSScriptRoot; Set-Location $sp; [Environment]::CurrentDirectory=$sp
. .\cdp.ps1; Connect-Cdp 9333; Size 1280 640
function Nav($u){ Cdp 'Page.navigate' @{url=$u} | Out-Null; Start-Sleep 4 }
Nav 'https://www.google.com/search?q=%E5%B9%AB%E9%99%8C%E7%94%9F%E4%BA%BA%E6%93%8D%E4%BD%9C%E6%89%8B%E6%A9%9F+%E7%94%9F%E7%89%A9%E7%89%B9%E5%BE%B5+%E6%9F%A5%E6%A0%B8&hl=zh-TW'
Js 'window.scrollTo(0,440); true' | Out-Null; Start-Sleep 1
$t = Js 'JSON.stringify(Array.from(document.querySelectorAll("a h3")).slice(0,5).map(function(h){var b=h.getBoundingClientRect();var c=h.closest("a").getBoundingClientRect();return {t:h.innerText.slice(0,30),x:Math.round(c.left),y:Math.round(c.top),w:Math.round(c.width),h:Math.round(c.height)}}))'
Set-Content 'shots\v1_g_results2.json' $t -Encoding utf8
Shot "$sp\shots\v1_g_results2.png"
Nav 'https://www.mygopen.com/2026/02/ai-fraud.html'
Js 'document.title' 
Shot "$sp\shots\v1_mgp.png"
Nav 'https://tfc-taiwan.org.tw/fact-check-reports/ai-biometric-fraud-claims-exaggerated'
Shot "$sp\shots\v1_tfc.png"
