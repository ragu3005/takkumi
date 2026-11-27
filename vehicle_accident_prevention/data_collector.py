# ============================================================
# data_collector.py — Simulation Data Collection & CSV Export
# Smart Vehicle Accident Prevention Simulation System
# ============================================================

import csv, os
import pandas as pd
from config import DATA_OUTPUT_DIR


class DataCollector:
    """
    Collects all simulation data and exports to CSV files.
    Also provides analysis summaries.
    """

    def __init__(self):
        os.makedirs(DATA_OUTPUT_DIR, exist_ok=True)
        self.all_scenario_results = []  # Stores summary of each speed scenario

    def save_vehicle_timeseries(self, vehicle, label: str):
        """Save per-timestep vehicle data to CSV."""
        filename = os.path.join(DATA_OUTPUT_DIR, f"timeseries_{label}kmh.csv")
        rows = []
        for i in range(len(vehicle.time_log)):
            rows.append({
                "time_s":          round(vehicle.time_log[i], 3),
                "speed_kmh":       round(vehicle.speed_log[i], 3),
                "position_m":      round(vehicle.position_log[i], 3),
                "acceleration":    round(vehicle.accel_log[i], 4),
                "braking_active":  vehicle.brake_log[i],
            })
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False)
        print(f"  📊 Time-series data saved: {filename}")
        return df

    def add_scenario_result(self, speed_kmh: int, vehicle, aeb, collision_detector):
        """Add summary result for one speed scenario."""
        col_summary = collision_detector.get_summary()
        aeb_report  = aeb.get_report()

        # Find actual stopping position
        final_pos = vehicle.position_log[-1] if vehicle.position_log else 0.0
        obstacle_x = collision_detector.obstacle_x
        clearance = obstacle_x - final_pos

        result = {
            "initial_speed_kmh":       speed_kmh,
            "obstacle_position_m":     obstacle_x,
            "vehicle_final_position_m": round(final_pos, 2),
            "clearance_m":             round(clearance, 2),
            "aeb_activated":           aeb_report["aeb_activated"],
            "aeb_trigger_distance_m":  aeb_report["trigger_distance_m"],
            "aeb_trigger_speed_kmh":   aeb_report["trigger_speed_kmh"],
            "aeb_trigger_time_s":      aeb_report["trigger_time_s"],
            "collision_occurred":      vehicle.collision_occurred,
            "theoretical_stop_dist_m": round(vehicle.stopping_distance_theoretical(), 2),
            "accident_prevented":      not vehicle.collision_occurred,
        }
        self.all_scenario_results.append(result)
        return result

    def save_all_scenarios(self):
        """Save combined results of all speed scenarios."""
        if not self.all_scenario_results:
            return
        filename = os.path.join(DATA_OUTPUT_DIR, "simulation_results_all.csv")
        df = pd.DataFrame(self.all_scenario_results)
        df.to_csv(filename, index=False)
        print(f"\n  📋 All scenario results saved: {filename}")
        return df

    def print_summary_table(self):
        """Print a readable summary table to console."""
        print("\n" + "="*70)
        print("  SIMULATION RESULTS SUMMARY")
        print("="*70)
        print(f"  {'Speed':>8} | {'Stop Dist':>10} | {'Clearance':>10} | "
              f"{'Collision':>10} | {'Prevented':>10}")
        print("-"*70)
        for r in self.all_scenario_results:
            print(f"  {r['initial_speed_kmh']:>5} km/h | "
                  f"  {r['theoretical_stop_dist_m']:>7.1f}m | "
                  f"  {r['clearance_m']:>7.1f}m | "
                  f"  {'YES' if r['collision_occurred'] else 'NO':>8}  | "
                  f"  {'✅ YES' if r['accident_prevented'] else '❌ NO':>8}")
        print("="*70)
