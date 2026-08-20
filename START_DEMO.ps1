# Meridyen arayüzü ile uyumlu demo başlatıcısı.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
$bundledPython = 'C:\Users\yolcu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if ($pythonCommand) {
    $pythonPath = $pythonCommand.Source
} elseif (Test-Path $bundledPython) {
    $pythonPath = $bundledPython
} else {
    throw 'Python bulunamadı. Python 3.11+ kurup bu komutu yeniden çalıştırın.'
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw 'Node.js / npm bulunamadı. Node.js LTS kurup bu komutu yeniden çalıştırın.'
}

Start-Process -FilePath $pythonPath -ArgumentList 'backend\run_server.py' -WorkingDirectory $root -WindowStyle Hidden
Start-Process powershell -ArgumentList '-NoExit', '-Command', "Set-Location '$root\frontend'; npm run dev"

Write-Host 'Backend: http://127.0.0.1:8000/docs'
Write-Host 'Site: Vite penceresindeki localhost adresinde (genellikle http://localhost:5173)'
