@echo off
echo Diagnostico de consumo en tiempo real para Dulce-Visor...
powershell -NoProfile -Command "Get-Process -Name 'pythonw', 'python' -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, @{Name='RAM_MB';Expression={[math]::Round($_.WorkingSet64 / 1MB, 2)}} | Format-Table -AutoSize"
pause
