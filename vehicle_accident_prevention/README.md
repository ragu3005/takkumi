# Smart Vehicle Accident Prevention & Simulation System Using Project Chrono and Python

## 1. Project Overview (திட்ட விளக்கம்)
இந்த Project-ன் முக்கிய நோக்கம் **Project Chrono 10.0 (3D Multi-Body Physics Engine)** மற்றும் **Python** பயன்படுத்தி ஒரு realistic 3D vehicle simulation உருவாக்குவது. 
Virtual road-ல் வாகனம் வெவ்வேறு வேகங்களில் (20 km/h, 40 km/h, 60 km/h) செல்லும்போது முன்னால் உள்ள தடையை (Obstacle) உணர்ந்து, தானாகவே **Automatic Emergency Braking (AEB)** இயங்கி விபத்தை தடுக்கும் (Accident Prevention).

---

## 2. Project Architecture & Files Structure

```
C:\Simulation System\
└── vehicle_accident_prevention\
    ├── config.py                 # Simulation constants, physics parameters & formulas
    ├── vehicle_model.py          # Vehicle physical properties & kinematics
    ├── road_terrain.py           # Road surface, friction & boundary model
    ├── obstacle_model.py         # Static obstacle position & dimensions
    ├── braking_system.py         # Automatic Emergency Braking (AEB) algorithm
    ├── collision_detection.py    # Real-time collision monitoring & logging
    ├── chrono_simulation.py      # Project Chrono (pychrono.core) 3D multi-body physics
    ├── data_collector.py         # Time-series & summary data export to CSV
    ├── graph_generator.py        # Matplotlib graphs (5 required analytical graphs)
    ├── simulate.py               # Main Project Chrono automated execution pipeline
    ├── main.py                   # System entry-point with fallback selector
    ├── run_simulation.bat        # One-click desktop execution script
    ├── data\                     # Output CSV files
    │   ├── timeseries_20kmh.csv
    │   ├── timeseries_40kmh.csv
    │   ├── timeseries_60kmh.csv
    │   └── simulation_results_all.csv
    └── graphs\                   # Generated visual plots (.png)
        ├── 01_speed_vs_time.png
        ├── 02_acceleration_vs_time.png
        ├── 03_position_vs_time.png
        ├── 04_braking_distance_vs_speed.png
        └── 05_scenario_comparison.png
```

---

## 3. Mathematical & Physics Formulas Used

### A. Braking Distance Calculation ($d_{brake}$):
$$d_{brake} = \frac{v^2}{2 \cdot \mu \cdot g}$$
- $v$: Vehicle Speed ($m/s$)
- $\mu$: Road Friction Coefficient ($0.7$ for dry asphalt)
- $g$: Acceleration due to gravity ($9.81\ m/s^2$)

### B. Driver / System Reaction Distance ($d_{reaction}$):
$$d_{reaction} = v \cdot t_{reaction}$$
- $t_{reaction} = 0.8\text{ seconds}$

### C. Safe Total Stopping Distance ($d_{safe}$):
$$d_{safe} = d_{brake} + d_{reaction} + \text{Safety Buffer (5m)}$$

---

## 4. Simulation Results Summary

| Initial Speed | Obstacle Position | Stopping Position | Clearance Margin | AEB Trigger Distance | Collision Occurred | Accident Prevented |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **20 km/h** | 80.0 m | 69.47 m | **10.53 m** | 11.63 m | **NO** | **✅ YES (Safe)** |
| **40 km/h** | 80.0 m | 61.26 m | **18.74 m** | 22.79 m | **NO** | **✅ YES (Safe)** |
| **60 km/h** | 80.0 m | 50.63 m | **29.37 m** | 38.49 m | **NO** | **✅ YES (Safe)** |

**Overall Safety Success Rate:** **100% (Accident Prevented in all 3 test speeds)**

---

## 5. How to Run (எப்படி இயக்குவது)

### Option 1: One-Click Run (மிகவும் எளிது)
Folder-ல் உள்ள [run_simulation.bat](file:///C:/Simulation%20System/vehicle_accident_prevention/run_simulation.bat) file-ஐ double click செய்யுங்கள்.

### Option 2: Terminal / CMD மூலம்
```cmd
cd "C:\Simulation System\vehicle_accident_prevention"
run_simulation.bat
```
அல்லது direct python command:
```cmd
set PATH=C:\Simulation System\chrono_env;C:\Simulation System\chrono_env\Library\bin;C:\Simulation System\chrono_env\Scripts;%PATH%
"C:\Simulation System\chrono_env\python.exe" simulate.py
```
