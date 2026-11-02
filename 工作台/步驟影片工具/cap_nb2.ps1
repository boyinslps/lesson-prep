. "$PSScriptRoot\cdp.ps1"
Connect-Cdp 9333
Size 1280 720
Cdp 'Emulation.setFocusEmulationEnabled' @{enabled=$true} | Out-Null
Cdp 'Page.setWebLifecycleState' @{state='active'} | Out-Null
$o="$PSScriptRoot\shots\nb"
function Click([int]$x,[int]$y){
  Cdp 'Input.dispatchMouseEvent' @{type='mouseMoved';x=$x;y=$y} | Out-Null
  Cdp 'Input.dispatchMouseEvent' @{type='mousePressed';x=$x;y=$y;button='left';clickCount=1} | Out-Null
  Cdp 'Input.dispatchMouseEvent' @{type='mouseReleased';x=$x;y=$y;button='left';clickCount=1} | Out-Null
}
function Home1 { Cdp 'Page.navigate' @{url='https://www.google.com/maps/search/%E5%AE%89%E5%B9%B3%E5%8F%A4%E5%A0%A1?hl=zh-TW&gl=TW'} | Out-Null; Start-Sleep 8
  Cdp 'Input.dispatchMouseEvent' @{type='mouseMoved';x=1000;y=300} | Out-Null; Start-Sleep 1 }
Home1; Shot "$o\b_place.png"
Click 708 37; Start-Sleep 6; Cdp 'Input.dispatchMouseEvent' @{type='mouseMoved';x=1000;y=300} | Out-Null; Start-Sleep 1; Shot "$o\b_spot.png"
Home1; Click 532 37; Start-Sleep 6; Cdp 'Input.dispatchMouseEvent' @{type='mouseMoved';x=1000;y=300} | Out-Null; Start-Sleep 1; Shot "$o\b_food.png"
Home1; Click 910 37; Start-Sleep 6; Cdp 'Input.dispatchMouseEvent' @{type='mouseMoved';x=1000;y=300} | Out-Null; Start-Sleep 1; Shot "$o\b_park.png"
Home1; Click 273 430; Start-Sleep 4; Shot "$o\b_near1.png"
