# RagGuard 国内镜像运行（Windows PowerShell）

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$env:HF_ENDPOINT = "https://hf-mirror.com"
$PipIndex = "https://pypi.tuna.tsinghua.edu.cn/simple"
$PipTrusted = "pypi.tuna.tsinghua.edu.cn"

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Pip = Join-Path $ProjectRoot ".venv\Scripts\pip.exe"

if (-not (Test-Path $Python)) {
    python -m venv .venv
}

& $Pip install -r requirements.txt -i $PipIndex --trusted-host $PipTrusted
& $Python -m ragguard.main --demo
