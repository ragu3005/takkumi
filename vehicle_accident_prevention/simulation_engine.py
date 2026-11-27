# ============================================================
# simulation_engine.py — Main Simulation Loop (Chrono-style)
# Smart Vehicle Accident Prevention Simulation System
# ============================================================

import sys, os
sys.path.insert(0, r"C:\Simulation System\vehicle_accident_prevention")

from config import (SIMULATION_TIMESTEP, SIMULATION_DURATION,
                    OBSTACLE_POSITION_X, TEST_SPEEDS_KMH)
from vehicle_model      import VehicleModel
from road_terrain       import RoadTerrain
from obstacle_model     import ObstacleModel
from braking_system     import AutoEmergencyBraking
from collision_detection import CollisionDetector
from data_collector     import DataCollector
from graph_generator    import GraphGenerator


def run_scenario(speed_kmh: int, road: RoadTerrain,
                 collector: DataCollector, grapher: GraphGenerator) -> dict:
    """
    Run a single simulation scenario for a given initial speed.
    Returns the scenario result summary dict.
    """
    print(f"\n{'='*60}")
    print(f"  🚗 SCENARIO: Initial Speed = {speed_kmh} km/h")
    print(f"{'='*60}")

    # --- Initialize all systems ---
    vehicle   = VehicleModel(initial_speed_kmh=speed_kmh)
    obstacle  = ObstacleModel(position_x=OBSTACLE_POSITION_X)
    aeb       = AutoEmergencyBraking()
    detector  = CollisionDetector(obstacle_x=OBSTACLE_POSITION_X)

    print(f"\n  Road: {road.length}m | Obstacle at: {obstacle.position_x}m")
    print(f"  Vehicle start speed: {speed_kmh} km/h "
          f"({vehicle.initial_speed:.2f} m/s)")

    # -------------------------------------------------------
    # Main Simulation Loop (replaces Chrono's DoStepDynamics)
    # Each iteration = SIMULATION_TIMESTEP seconds of physics
    # -------------------------------------------------------
    t = 0.0
    dt = SIMULATION_TIMESTEP

    while t <= SIMULATION_DURATION:
        # 1. AEB check — should we brake?
        aeb_status = aeb.check_and_brake(vehicle, obstacle.position_x, t)

        # 2. Collision check
        if detector.check_collision(vehicle, t):
            print(f"  ⚠️  Simulation ended: COLLISION at t={t:.2f}s")
            vehicle.update(dt)   # one more step to record final state
            break

        # 3. Update vehicle physics
        vehicle.update(dt)

        # 4. Check if vehicle stopped safely
        if vehicle.stopped:
            dist_to_obs = vehicle.get_distance_to_obstacle(obstacle.position_x)
            print(f"\n  ✅ Vehicle stopped safely!")
            print(f"     Final position: {vehicle.position_x:.2f}m")
            print(f"     Distance to obstacle: {dist_to_obs:.2f}m")
            break

        # 5. Check if vehicle passed road end without incident
        if vehicle.position_x >= road.length:
            print(f"  ℹ️  Vehicle reached road end without incident.")
            break

        t += dt

    # --- Collect data ---
    collector.save_vehicle_timeseries(vehicle, label=str(speed_kmh))
    result = collector.add_scenario_result(speed_kmh, vehicle, aeb, detector)
    grapher.add_scenario(speed_kmh, vehicle, result)

    # Save collision log if any
    detector.save_collision_log(str(speed_kmh))

    return result


def run_full_simulation():
    """
    Run the complete simulation for all 3 speed scenarios.
    """
    print("\n" + "🚗"*30)
    print("  SMART VEHICLE ACCIDENT PREVENTION SIMULATION SYSTEM")
    print("  Powered by Physics-based Kinematic Simulation Engine")
    print("🚗"*30)

    # --- Setup shared environment ---
    road      = RoadTerrain()
    collector = DataCollector()
    grapher   = GraphGenerator()

    # --- Run each speed scenario ---
    all_results = []
    for speed in TEST_SPEEDS_KMH:
        result = run_scenario(speed, road, collector, grapher)
        all_results.append(result)

    # --- Save combined results ---
    collector.save_all_scenarios()
    collector.print_summary_table()

    # --- Generate all graphs ---
    grapher.generate_all()

    # --- Final verdict ---
    print("\n" + "🏁"*30)
    print("  FINAL RESULTS")
    print("🏁"*30)
    for r in all_results:
        status = "✅ ACCIDENT PREVENTED" if r["accident_prevented"] else "❌ COLLISION OCCURRED"
        print(f"  {r['initial_speed_kmh']:>3} km/h → {status} "
              f"| Clearance: {r['clearance_m']:.1f}m")

    print(f"\n  📁 Data saved to : C:\\Simulation System\\vehicle_accident_prevention\\data\\")
    print(f"  📁 Graphs saved to: C:\\Simulation System\\vehicle_accident_prevention\\graphs\\")
    print("\n  Simulation Complete! ✅")

    return all_results


if __name__ == "__main__":
    run_full_simulation()
