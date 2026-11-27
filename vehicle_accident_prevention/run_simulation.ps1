Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "  Smart Vehicle Accident Prevention System (Project Chrono 10)" -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host ""

$env:PATH = "C:\Simulation System\chrono_env;C:\Simulation System\chrono_env\Library\bin;C:\Simulation System\chrono_env\Scripts;" + $env:PATH
& "C:\Simulation System\chrono_env\python.exe" "C:\Simulation System\vehicle_accident_prevention\simulate.py"

Write-Host ""
Write-Host "===================================================================" -ForegroundColor Green
Write-Host "Simulation run finished!" -ForegroundColor Green
Write-Host "===================================================================" -ForegroundColor Green
