# ============================================================
# main.py — Project Entry Point
# Smart Vehicle Accident Prevention Simulation System
# ============================================================

import sys, os

PROJECT_DIR = r"C:\Simulation System\vehicle_accident_prevention"
sys.path.insert(0, PROJECT_DIR)

def check_dependencies():
    """Check all required packages are installed."""
    required = {
        'numpy':      'numpy',
        'pandas':     'pandas',
        'matplotlib': 'matplotlib',
    }
    missing = []
    for pkg, imp in required.items():
        try:
            __import__(imp)
            print(f"  ✅ {pkg}")
        except ImportError:
            print(f"  ❌ {pkg} — MISSING!")
            missing.append(pkg)

    # Project Chrono check
    try:
        import pychrono.core as chrono
        print(f"  ✅ pychrono.core (Official Project Chrono 10.0) — 3D physics ready!")
        return missing, True
    except ImportError:
        print(f"  ⚠️  pychrono not found in current environment — using kinematic engine")
        return missing, False

def main():
    print("\n" + "="*65)
    print("  🚗 SMART VEHICLE ACCIDENT PREVENTION SIMULATION")
    print("  Powered by Project Chrono 3D Multi-Body Physics")
    print("="*65)

    print("\n📦 Checking dependencies...")
    missing, chrono_available = check_dependencies()

    if missing:
        print(f"\n❌ Install missing packages: pip install {' '.join(missing)}")
        sys.exit(1)

    print(f"\n🔬 Active Physics Engine: {'Project Chrono 10.0 (3D Multi-Body)' if chrono_available else 'Kinematic Physics Engine'}")
    print("🚀 Running simulation scenarios (20 km/h, 40 km/h, 60 km/h)...\n")

    if chrono_available:
        # --- Run using Official Project Chrono ---
        from chrono_simulation import run_chrono_scenario
        from data_collector import DataCollector
        from graph_generator import GraphGenerator
        from config import TEST_SPEEDS_KMH, OBSTACLE_POSITION_X

        collector = DataCollector()
        grapher   = GraphGenerator()
        all_results = []

        for speed in TEST_SPEEDS_KMH:
            print(f"\n{'='*60}")
            print(f"  🚗 CHRONO SCENARIO: Initial Speed = {speed} km/h")
            print(f"{'='*60}")

            result = run_chrono_scenario(speed)
            vehicle = result.pop('vehicle')
            aeb     = result.pop('aeb')

            # Save timeseries data
            collector.save_vehicle_timeseries(vehicle, label=str(speed))

            from collision_detection import CollisionDetector
            detector = CollisionDetector(OBSTACLE_POSITION_X)
            detector.collision_events = []
            if result['collision_occurred']:
                detector.collision_events.append({
                    'time_s': 0, 'position_m': result['vehicle_final_position_m'],
                    'impact_speed_kmh': speed, 'distance_at_impact_m': 0,
                    'initial_speed_kmh': speed
                })

            final_result = collector.add_scenario_result(speed, vehicle, aeb, detector)
            grapher.add_scenario(speed, vehicle, final_result)
            all_results.append(final_result)

        collector.save_all_scenarios()
        collector.print_summary_table()
        grapher.generate_all()

    else:
        # --- Fallback Kinematic Engine ---
        from simulation_engine import run_full_simulation
        all_results = run_full_simulation()

    # Final summary verdict
    print("\n" + "🏁"*32)
    print("  SIMULATION FINAL VERDICT & SAFETY REPORT")
    print("🏁"*32)
    accidents_prevented = sum(1 for r in all_results if r.get('accident_prevented', False))
    total = len(all_results)

    for r in all_results:
        status = "✅ ACCIDENT PREVENTED" if r["accident_prevented"] else "❌ COLLISION"
        print(f"  Speed {r['initial_speed_kmh']:>2} km/h: {status} | Final Distance to Obstacle: {r['clearance_m']:.2f}m")

    print(f"\n  Accidents Prevented: {accidents_prevented}/{total} scenarios")
    print(f"  Overall Safety Rating: {accidents_prevented/total*100:.0f}%")

    if accidents_prevented == total:
        print("\n  🏆 SUCCESS: Automatic Emergency Braking (AEB) prevented ALL collisions!")
    else:
        print(f"\n  ⚠️  AEB prevented {accidents_prevented} of {total} accidents.")

    print(f"\n  📁 CSV Datasets: C:\\Simulation System\\vehicle_accident_prevention\\data\\")
    print(f"  📁 Visual Graphs: C:\\Simulation System\\vehicle_accident_prevention\\graphs\\")
    print("\n  Simulation Execution Complete! ✅\n")


if __name__ == "__main__":
    main()
