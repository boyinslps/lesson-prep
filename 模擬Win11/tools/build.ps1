# 重新建置模擬 Windows 11（產生 dist/）。需要 Node：用 工作台\runtime\node（可攜版）。
# 用法：powershell -File 模擬Win11\tools\build.ps1
$ErrorActionPreference = "Stop"
$pkg = Split-Path -Parent $PSScriptRoot
$root = Split-Path -Parent $pkg
$node = Join-Path $root "工作台\runtime\node"
if (-not (Test-Path (Join-Path $node "node.exe"))) {
  Write-Host "找不到 $node\node.exe。請照 模擬Win11\AI說明.md「建置環境」安裝可攜版 Node（v22 LTS，win-x64 zip）解壓縮到該資料夾。"
  exit 1
}
$env:PATH = "$node;$env:PATH"
$env:CI = "false"
Set-Location $pkg
if (-not (Test-Path "node_modules")) { & "$node\npm.cmd" install --no-audit --no-fund }
& "$node\npx.cmd" react-scripts build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "完成：$pkg\dist"
