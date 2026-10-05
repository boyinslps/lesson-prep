param([string]$spec, [string]$out)
# 把 JSON 規格渲染成逐格 PNG，再用 ffmpeg 合成 MP4（H.264、yuv420p、faststart，網頁可直接播）
$ErrorActionPreference = 'Stop'
$sp = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $sp; [Environment]::CurrentDirectory = $sp
if (-not ('StepVideo' -as [type])) {
  Add-Type -Path "$sp\StepVideo.cs" -ReferencedAssemblies System.Drawing, System.Web.Extensions
}
$frames = Join-Path $sp ("frames_" + [IO.Path]::GetFileNameWithoutExtension($out))
if (Test-Path $frames) { Remove-Item $frames -Recurse -Force }
$n = [StepVideo]::Render((Resolve-Path $spec).Path, $frames)
"frames=$n"
& "C:\Users\Roki\tools\ffmpeg\bin\ffmpeg.exe" -hide_banner -loglevel error -y -framerate 25 -i "$frames\f%05d.png" -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p -movflags +faststart $out
"mp4=" + (Get-Item $out).Length
