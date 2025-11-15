$ErrorActionPreference = "Stop"

param(
    [string]$PythonExe = "python",
    [string]$VenvPath = ".venv"
)

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Write-Host ">>> 仓库根目录：$RepoRoot" -ForegroundColor Cyan

Write-Host ">>> 使用 $PythonExe 创建/更新虚拟环境：$VenvPath" -ForegroundColor Cyan
if (-not (Test-Path $VenvPath)) {
    & $PythonExe -m venv $VenvPath
} else {
    Write-Host "虚拟环境已存在，跳过创建。" -ForegroundColor Yellow
}

$venvPython = Join-Path $VenvPath "Scripts" "python.exe"
if (-not (Test-Path $venvPython)) {
    throw "未在 $VenvPath 中找到 python，可尝试删除该目录后重新执行脚本。"
}

Write-Host ">>> 升级 pip" -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip

$pyproject = Join-Path $RepoRoot "pyproject.toml"
if (Test-Path $pyproject) {
    Write-Host ">>> 检测到 pyproject.toml，执行 pip install -e \".[dev]\"" -ForegroundColor Cyan
    Push-Location $RepoRoot
    & $venvPython -m pip install -e ".[dev]"
    Pop-Location
} else {
    Write-Host ">>> 未发现 pyproject.toml，仅安装工具依赖（ruff/black/pytest）" -ForegroundColor Yellow
    & $venvPython -m pip install ruff black pytest
}

Write-Host ">>> 开发环境准备完毕，请执行 `& $venvPython -m pip list` 确认安装情况。" -ForegroundColor Green
