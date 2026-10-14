$ErrorActionPreference='Stop'
$sp=$PSScriptRoot; Set-Location $sp; [Environment]::CurrentDirectory=$sp
. .\cdp.ps1; Connect-Cdp 9333; Size 1280 640
function Nav($u){ Cdp 'Page.navigate' @{url=$u} | Out-Null; Start-Sleep 4 }
# 1 訊息
Nav ('file:///'+($sp.Replace([string][char]92,'/'))+'/v1_msg.html')
$r = Js 'JSON.stringify(["k1","k2","k3"].map(function(i){var b=document.getElementById(i).getBoundingClientRect();return {id:i,x:Math.round(b.left),y:Math.round(b.top),w:Math.round(b.width),h:Math.round(b.height)}}))'
Set-Content 'shots\v1_rects.json' $r -Encoding utf8
Shot "$sp\shots\v1_msg.png"
# 2 Google 首頁 + 輸入
Nav 'https://www.google.com/?hl=zh-TW'
Js 'var q=document.querySelector("textarea[name=q],input[name=q]"); q.focus(); true' | Out-Null
Cdp 'Input.insertText' @{text='幫陌生人操作手機 生物特徵 查核'} | Out-Null
Start-Sleep 1
$b = Js 'var q=document.querySelector("textarea[name=q],input[name=q]").getBoundingClientRect(); JSON.stringify({x:Math.round(q.left),y:Math.round(q.top),w:Math.round(q.width),h:Math.round(q.height)})'
Set-Content 'shots\v1_g_box.json' $b -Encoding utf8
Shot "$sp\shots\v1_g_typed.png"
# 3 結果
Nav 'https://www.google.com/search?q=%E5%B9%AB%E9%99%8C%E7%94%9F%E4%BA%BA%E6%93%8D%E4%BD%9C%E6%89%8B%E6%A9%9F+%E7%94%9F%E7%89%A9%E7%89%B9%E5%BE%B5+%E6%9F%A5%E6%A0%B8&hl=zh-TW'
Js 'document.title + " | " + location.href'
$t = Js 'JSON.stringify(Array.from(document.querySelectorAll("a h3")).slice(0,8).map(function(h){var a=h.closest("a");var b=h.getBoundingClientRect();return {t:h.innerText,u:a.href.slice(0,70),x:Math.round(b.left),y:Math.round(b.top),w:Math.round(b.width),h:Math.round(b.height)}}))'
Set-Content 'shots\v1_g_results.json' $t -Encoding utf8
Shot "$sp\shots\v1_g_results.png"
