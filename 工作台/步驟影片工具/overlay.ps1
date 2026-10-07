param([string]$spec, [string]$out)
# 把字卡／按鍵／紅框疊到老師自己錄的影片上（影片放上方 1280x720，下方 140px 字卡）
$ErrorActionPreference = 'Stop'
$sp = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $sp; [Environment]::CurrentDirectory = $sp
Add-Type -Path "$sp\StepVideo.cs" -ReferencedAssemblies System.Drawing, System.Web.Extensions
$od = Join-Path $sp ("frames_" + [IO.Path]::GetFileNameWithoutExtension($out))
if (Test-Path $od) { Remove-Item $od -Recurse -Force }
$specPath = (Resolve-Path $spec).Path
$n = [StepVideo]::RenderOverlays($specPath, $od)
$j = Get-Content $specPath -Raw -Encoding UTF8 | ConvertFrom-Json
$src = Join-Path (Resolve-Path "$sp\..\..").Path $j.source
$inputs = @('-i', $src)
# keep：只保留這些片段（[[開始,結束],…]，秒）再接起來；fit：等比例縮放、上下補邊（錄影不是 16:9 時用）
$scale = if ($j.fit) { "scale=1280:-2,pad=1280:720:0:(720-ih)/2:color=0xffffff" } else { "scale=1280:720" }
if ($j.keep) {
  $parts = @(); $k = 0
  foreach ($seg in $j.keep) { $parts += "[0:v]trim=$($seg[0]):$($seg[1]),setpts=PTS-STARTPTS[k$k]"; $k++ }
  $cat = (0..($k-1) | ForEach-Object { "[k$_]" }) -join ''
  $fc = ($parts -join ';') + ";$cat" + "concat=n=$($k):v=1:a=0,$scale,pad=1280:860:0:0:color=0x1e1b4b[v0]"
} else {
  $fc = "[0:v]trim=0:$($j.cut),setpts=PTS-STARTPTS,$scale,pad=1280:860:0:0:color=0x1e1b4b[v0]"
}
$last = 'v0'
for ($i = 0; $i -lt $n; $i++) {
  $inputs += @('-i', (Join-Path $od ("o{0:D2}.png" -f $i)))
  $s = $j.scenes[$i]
  $fc += ";[$last][$($i+1):v]overlay=0:0:enable='between(t,$($s.from),$($s.to))'[v$($i+1)]"
  $last = "v$($i+1)"
}
& "C:\Users\Roki\tools\ffmpeg\bin\ffmpeg.exe" -hide_banner -loglevel error -y @inputs -filter_complex $fc -map "[$last]" -an -r 25 -c:v libx264 -preset slow -crf 24 -pix_fmt yuv420p -movflags +faststart $out
"overlays=$n mp4=" + (Get-Item $out).Length
