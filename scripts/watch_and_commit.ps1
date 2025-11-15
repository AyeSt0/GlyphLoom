param(
    [string]$PythonExe = "python",
    [int]$DebounceSeconds = 3
)

$ErrorActionPreference = "Stop"

$script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$script:AutoCommitScript = Join-Path $RepoRoot "scripts" "auto_commit.py"
$script:GitDirectory = Join-Path $RepoRoot ".git"
$script:VersionFile = Join-Path $RepoRoot "VERSION"

if (-not (Test-Path $AutoCommitScript)) {
    throw "自动提交脚本不存在：$AutoCommitScript"
}

if (-not (Test-Path $GitDirectory)) {
    throw "当前目录不是有效的 Git 仓库：$RepoRoot"
}

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $RepoRoot
$watcher.Filter = "*"
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

$timer = New-Object System.Timers.Timer
$timer.Interval = $DebounceSeconds * 1000
$timer.AutoReset = $false

$handlers = @()

function Invoke-AutoCommit {
    Write-Host "检测到文件保存，准备自动提交..." -ForegroundColor Cyan
    $proc = Start-Process -FilePath $PythonExe `
        -ArgumentList @($AutoCommitScript) `
        -WorkingDirectory $RepoRoot `
        -NoNewWindow `
        -Wait `
        -PassThru

    if ($proc.ExitCode -ne 0) {
        Write-Warning "自动提交失败（退出码 $($proc.ExitCode)），请手动检查。"
    }
}

$script:DebounceAction = {
    param($Sender, $EventArgs)
    $path = $EventArgs.FullPath
    if ($null -ne $path) {
        if ($path.StartsWith($script:GitDirectory)) { return }
        if ($path -eq $script:VersionFile) { return }
    }
    $timer.Stop()
    $timer.Start()
}

$handlers += Register-ObjectEvent -InputObject $watcher -EventName Changed -SourceIdentifier "auto-commit-changed" -Action $DebounceAction
$handlers += Register-ObjectEvent -InputObject $watcher -EventName Created -SourceIdentifier "auto-commit-created" -Action $DebounceAction
$handlers += Register-ObjectEvent -InputObject $watcher -EventName Deleted -SourceIdentifier "auto-commit-deleted" -Action $DebounceAction
$handlers += Register-ObjectEvent -InputObject $watcher -EventName Renamed -SourceIdentifier "auto-commit-renamed" -Action $DebounceAction

$handlers += Register-ObjectEvent -InputObject $timer -EventName Elapsed -SourceIdentifier "auto-commit-elapsed" -Action {
    Invoke-AutoCommit
}

Write-Host "自动监听已启动（$RepoRoot）。保存后会在 $DebounceSeconds 秒内尝试自动提交，按 Ctrl+C 退出。" -ForegroundColor Green

try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    foreach ($handler in $handlers) {
        Unregister-Event -SourceIdentifier $handler.Name
    }
    $watcher.EnableRaisingEvents = $false
    $watcher.Dispose()
    $timer.Dispose()
    Write-Host "已停止自动监听。"
}
