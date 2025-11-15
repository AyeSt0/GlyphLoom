$ErrorActionPreference = "Stop"

param(
    [string]$PythonExe = "python",
    [switch]$Quiet
)

$commands = @(
    @{ Title = "ruff"; Args = @("-m", "ruff", "check", ".") },
    @{ Title = "black"; Args = @("-m", "black", "--check", ".") },
    @{ Title = "pytest"; Args = @("-m", "pytest", "-q") }
)

foreach ($cmd in $commands) {
    $title = $cmd.Title
    $args = $cmd.Args
    if (-not $Quiet) {
        Write-Host ">>> 运行 $title ..." -ForegroundColor Cyan
    }
    $proc = Start-Process -FilePath $PythonExe -ArgumentList $args -Wait -PassThru -NoNewWindow
    if ($proc.ExitCode -ne 0) {
        throw "$title 执行失败，退出码 $($proc.ExitCode)"
    }
}

Write-Host ">>> 质量检查全部通过" -ForegroundColor Green
