$ErrorActionPreference='Stop'
$sp=$PSScriptRoot; Set-Location $sp; [Environment]::CurrentDirectory=$sp
. .\cdp.ps1; Connect-Cdp 9333; Size 1280 640
$page = 'file:///D:/%E8%87%AA%E5%8B%95%E5%8C%96%E6%95%99%E6%A1%88%E7%94%9F%E6%88%90%E5%B7%A5%E4%BD%9C%E6%B5%81/materials/%E7%89%B9%E6%95%99%E6%94%AF%E6%8C%81/%E4%BA%94%E4%B8%8A_%E6%9F%A5%E8%AD%89%E5%B0%8F%E5%81%B5%E6%8E%A2_%E7%89%B9%E6%95%99%E7%89%88/%E4%BA%94%E4%B8%8A_%E6%9F%A5%E8%AD%89%E5%B0%8F%E5%81%B5%E6%8E%A2_%E7%89%B9%E6%95%99%E7%89%88.html'
Cdp 'Page.navigate' @{url=$page} | Out-Null; Start-Sleep 3
$all=@{}
$states=@{ k0='{}'; k1='{"0":1}'; k2='{"0":1,"1":1}'; k3='{"0":1,"1":1,"4":1}'; k4='{"0":1,"1":1,"4":1}' }
foreach($s in 'k0','k1','k2','k3','k4'){
  $cp = if($s -eq 'k4'){1}else{0}
  $js = 'localStorage.setItem("sp_detective_v1", JSON.stringify({i:2,kw:[' + $states[$s] + ',{}],copied:[' + $cp + ',0],ack:{},org:[{},{}],judged:[0,0],pick:[null,null]})); true'
  Js $js | Out-Null; Cdp "Page.navigate" @{url=$page} | Out-Null; Start-Sleep 3
  Js 'document.body.style.zoom=0.66; document.querySelector("nav.bar").style.display="none"; document.querySelector(".sig").style.display="none"; window.scrollTo(0,0); true' | Out-Null; Start-Sleep 1
  $all[$s] = Js 'JSON.stringify((function(){var o={};["[data-w=\"0\"]","[data-w=\"1\"]","[data-w=\"4\"]","#copyBtn",".slots"].forEach(function(q){var e=document.querySelector(q);if(e){var b=e.getBoundingClientRect();o[q]={x:Math.round(b.left),y:Math.round(b.top),w:Math.round(b.width),h:Math.round(b.height)};}});return o})())'
  Shot "$sp\shots\sp_kw_$s.png"
}
($all | ConvertTo-Json) | Set-Content 'shots\sp_kw_rects.json' -Encoding utf8
Js 'localStorage.removeItem("sp_detective_v1"); true' | Out-Null
"done"
