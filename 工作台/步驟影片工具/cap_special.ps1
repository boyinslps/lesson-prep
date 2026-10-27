$ErrorActionPreference='Stop'
$sp=$PSScriptRoot; Set-Location $sp; [Environment]::CurrentDirectory=$sp
. .\cdp.ps1; Connect-Cdp 9333; Size 1280 640
function Nav($u,$w=4){ Cdp 'Page.navigate' @{url=$u} | Out-Null; Start-Sleep $w }
$q = '手機充電 講電話 喝水 查核'
# 1 Google 首頁（空）與貼上關鍵字
Nav 'https://www.google.com/?hl=zh-TW'
Shot "$sp\shots\sp_g_empty.png"
$b0 = Js 'var q=document.querySelector("textarea[name=q],input[name=q]").getBoundingClientRect(); JSON.stringify({x:Math.round(q.left),y:Math.round(q.top),w:Math.round(q.width),h:Math.round(q.height)})'
Set-Content 'shots\sp_g_box.json' $b0 -Encoding utf8
Js 'var q=document.querySelector("textarea[name=q],input[name=q]"); q.focus(); true' | Out-Null
Cdp 'Input.insertText' @{text=$q} | Out-Null
Start-Sleep 1
Shot "$sp\shots\sp_g_typed.png"
# 2 搜尋結果
$u = 'https://www.google.com/search?hl=zh-TW&q=' + [Uri]::EscapeDataString($q)
Nav $u 5
Js 'document.title + " | " + location.href'
$t = Js 'JSON.stringify(Array.from(document.querySelectorAll("a h3")).slice(0,8).map(function(h){var a=h.closest("a");var b=h.getBoundingClientRect();var c=a.getBoundingClientRect();return {t:h.innerText.slice(0,40),u:a.href.slice(0,80),x:Math.round(c.left),y:Math.round(c.top),w:Math.round(c.width),h:Math.round(c.height)}}))'
Set-Content 'shots\sp_g_results.json' $t -Encoding utf8
Shot "$sp\shots\sp_g_results.png"
# 3 報告頁
Nav 'https://www.mygopen.com/2022/01/Charging-Phone.html' 5
Js 'document.title'
Shot "$sp\shots\sp_mgp_H.png"
Nav 'https://tfc-taiwan.org.tw/fact-check-reports/migration-6824' 5
Js 'document.title'
Shot "$sp\shots\sp_tfc_H.png"
Nav 'https://tfc-taiwan.org.tw/?p=109294' 5
Js 'document.title + " | " + location.href'
Shot "$sp\shots\sp_tfc_D.png"
