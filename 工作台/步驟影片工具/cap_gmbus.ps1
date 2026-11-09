. "$PSScriptRoot\cdp.ps1"
Connect-Cdp 9333
Size 1280 720
Cdp 'Emulation.setFocusEmulationEnabled' @{enabled=$true} | Out-Null
Cdp 'Page.setWebLifecycleState' @{state='active'} | Out-Null
$o="$PSScriptRoot\shots\gmbus"
function Click([int]$x,[int]$y){
  Cdp 'Input.dispatchMouseEvent' @{type='mouseMoved';x=$x;y=$y} | Out-Null
  Cdp 'Input.dispatchMouseEvent' @{type='mousePressed';x=$x;y=$y;button='left';clickCount=1} | Out-Null
  Cdp 'Input.dispatchMouseEvent' @{type='mouseReleased';x=$x;y=$y;button='left';clickCount=1} | Out-Null
}
function Away { Cdp 'Input.dispatchMouseEvent' @{type='mouseMoved';x=1000;y=520} | Out-Null; Start-Sleep 1 }
# \u6797\u767e\u8ca8 -> \u8d64\u5d01\u6a13
Cdp 'Page.navigate' @{url='https://www.google.com/maps/dir/%E6%9E%97%E7%99%BE%E8%B2%A8/%E8%B5%A4%E5%B4%81%E6%A8%93/?hl=zh-TW&gl=TW'} | Out-Null
Start-Sleep 9; Away; Shot "$o\s0_form.png"
Click 300 49; Start-Sleep 5; Away; Shot "$o\s1_transit.png"
Click 174 437; Start-Sleep 4; Away; Shot "$o\s2_detail.png"
