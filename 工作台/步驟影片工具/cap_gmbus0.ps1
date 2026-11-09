. "$PSScriptRoot\cdp.ps1"
Connect-Cdp 9333
Size 1280 720
Cdp 'Emulation.setFocusEmulationEnabled' @{enabled=$true} | Out-Null
Cdp 'Page.setWebLifecycleState' @{state='active'} | Out-Null
$o="$PSScriptRoot\shots\gmbus"
Cdp 'Page.navigate' @{url='https://www.google.com/maps/dir/%E6%9E%97%E7%99%BE%E8%B2%A8/%E8%B5%A4%E5%B4%81%E6%A8%93/data=!4m2!4m1!3e0?hl=zh-TW&gl=TW'} | Out-Null
Start-Sleep 9
Cdp 'Input.dispatchMouseEvent' @{type='mouseMoved';x=1000;y=520} | Out-Null; Start-Sleep 1
Shot "$o\s0_form.png"
