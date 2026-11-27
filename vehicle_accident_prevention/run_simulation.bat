@echo off
title Smart Vehicle Accident Prevention Simulation System
echo ===================================================================
echo   Smart Vehicle Accident Prevention System (Project Chrono 10)
echo ===================================================================
echo.

set PATH=C:\Simulation System\chrono_env;C:\Simulation System\chrono_env\Library\bin;C:\Simulation System\chrono_env\Scripts;%PATH%
"C:\Simulation System\chrono_env\python.exe" "C:\Simulation System\vehicle_accident_prevention\simulate.py"

echo.
echo ===================================================================
echo Simulation run finished! Press any key to exit.
echo ===================================================================
pause
