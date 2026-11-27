# ============================================================
# simulate.py — Project Chrono Accident Prevention Simulation
# Complete Automated Runner & Validator
# ============================================================

import sys, os
sys.path.insert(0, r"C:\Simulation System\vehicle_accident_prevention")

from config import TEST_SPEEDS_KMH, OBSTACLE_POSITION_X
from chrono_simulation import run_chrono_scenario
from data_collector import DataCollector
from graph_generator import GraphGenerator
from collision_detection import CollisionDetector

def run_project():
    print("=" * 68)
    print("  SMART VEHICLE ACCIDENT PREVENTION & SIMULATION SYSTEM")
    print("  Engine: Official Project Chrono 10.0 (pychrono.core)")
    print("=" * 68)

    collector = DataCollector()
    grapher = GraphGenerator()
    all_results = []

    for speed in TEST_SPEEDS_KMH:
        print(f"\n{'-'*65}")
        print(f"  >>> RUNNING PROJECT CHRONO SIMULATION: {speed} km/h <<<")
        print(f"{'-'*65}")

        scenario_res = run_chrono_scenario(speed)
        vehicle = scenario_res.pop('vehicle')
        aeb = scenario_res.pop('aeb')

        # Save detailed time series
        collector.save_vehicle_timeseries(vehicle, label=str(speed))

        # Collision detection recording
        detector = CollisionDetector(OBSTACLE_POSITION_X)
        if scenario_res['collision_occurred']:
            detector.collision_events.append({
                'time_s': vehicle.time_log[-1] if vehicle.time_log else 0,
                'position_m': scenario_res['vehicle_final_position_m'],
                'impact_speed_kmh': speed,
                'distance_at_impact_m': 0,
                'initial_speed_kmh': speed
            })

        final_res = collector.add_scenario_result(speed, vehicle, aeb, detector)
        grapher.add_scenario(speed, vehicle, final_res)
        all_results.append(final_res)

    # Export all summary results to CSV
    collector.save_all_scenarios()
    collector.print_summary_table()

    # Generate all graphs
    grapher.generate_all()

    print("\n" + "=" * 68)
    print("  ALL SIMULATION SCENARIOS FINISHED SUCCESSFULLY!")
    print("=" * 68)
    for r in all_results:
        verdict = "[PREVENTED]" if r["accident_prevented"] else "[CRASH]"
        print(f"  Speed {r['initial_speed_kmh']:>2} km/h -> {verdict} | Stopping Pos: {r['vehicle_final_position_m']:.2f}m | Obstacle: {r['obstacle_position_m']}m | Margin: {r['clearance_m']:.2f}m")

    print("\nDone!")

if __name__ == "__main__":
    run_project()
