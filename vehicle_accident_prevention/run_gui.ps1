$env:PATH = "C:\Simulation System\chrono_env;C:\Simulation System\chrono_env\Library\bin;C:\Simulation System\chrono_env\Scripts;" + $env:PATH
Start-Process -FilePath "C:\Simulation System\chrono_env\pythonw.exe" -ArgumentList '"C:\Simulation System\vehicle_accident_prevention\gui_app.py"'
Write-Host "GUI Simulation Window Launched! Check your taskbar." -ForegroundColor Green
