# ============================================================
# graph_generator.py — Matplotlib Graph Generation
# Smart Vehicle Accident Prevention Simulation System
# ============================================================

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import os
from config import GRAPH_OUTPUT_DIR, OBSTACLE_POSITION_X

COLORS = {20: '#2ecc71', 40: '#f39c12', 60: '#e74c3c'}
LABELS = {20: '20 km/h', 40: '40 km/h', 60: '60 km/h'}


class GraphGenerator:
    """Generates all required Matplotlib graphs for the simulation."""

    def __init__(self):
        os.makedirs(GRAPH_OUTPUT_DIR, exist_ok=True)
        self.vehicles = {}
        self.results = []

    def add_scenario(self, speed_kmh: int, vehicle, result: dict):
        self.vehicles[speed_kmh] = vehicle
        self.results.append(result)

    def plot_speed_vs_time(self):
        fig, ax = plt.subplots(figsize=(10, 5))
        for spd, veh in self.vehicles.items():
            ax.plot(veh.time_log, veh.speed_log,
                    color=COLORS[spd], linewidth=2,
                    label=LABELS[spd])
            if veh.braking_applied and veh.brake_start_time:
                bt = veh.brake_start_time
                bs = veh.initial_speed * 3.6
                ax.axvline(x=bt, color=COLORS[spd], linestyle='--', alpha=0.5)
                ax.annotate(f'Brake\n{spd}km/h',
                            xy=(bt, bs), fontsize=8, color=COLORS[spd])

        ax.set_title('Speed vs Time - Project Chrono AEB Simulation',
                     fontsize=13, fontweight='bold')
        ax.set_xlabel('Time (seconds)', fontsize=11)
        ax.set_ylabel('Speed (km/h)', fontsize=11)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(bottom=0)
        plt.tight_layout()
        path = os.path.join(GRAPH_OUTPUT_DIR, '01_speed_vs_time.png')
        plt.savefig(path, dpi=150)
        plt.close()
        print(f"  📈 Graph saved: {path}")

    def plot_acceleration_vs_time(self):
        fig, ax = plt.subplots(figsize=(10, 5))
        for spd, veh in self.vehicles.items():
            ax.plot(veh.time_log, veh.accel_log,
                    color=COLORS[spd], linewidth=2, label=LABELS[spd])

        ax.axhline(y=0, color='black', linewidth=0.8, linestyle='-')
        ax.set_title('Acceleration vs Time - Emergency Braking (Project Chrono)',
                     fontsize=13, fontweight='bold')
        ax.set_xlabel('Time (seconds)', fontsize=11)
        ax.set_ylabel('Acceleration (m/s^2)', fontsize=11)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        path = os.path.join(GRAPH_OUTPUT_DIR, '02_acceleration_vs_time.png')
        plt.savefig(path, dpi=150)
        plt.close()
        print(f"  📈 Graph saved: {path}")

    def plot_distance_vs_time(self):
        fig, ax = plt.subplots(figsize=(10, 5))
        for spd, veh in self.vehicles.items():
            ax.plot(veh.time_log, veh.position_log,
                    color=COLORS[spd], linewidth=2, label=LABELS[spd])

        ax.axhline(y=OBSTACLE_POSITION_X, color='red', linewidth=2,
                   linestyle='--', label=f'Obstacle @ {OBSTACLE_POSITION_X}m')

        ax.set_title('Vehicle Position vs Time (Project Chrono Dynamics)',
                     fontsize=13, fontweight='bold')
        ax.set_xlabel('Time (seconds)', fontsize=11)
        ax.set_ylabel('Position (meters from start)', fontsize=11)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        path = os.path.join(GRAPH_OUTPUT_DIR, '03_position_vs_time.png')
        plt.savefig(path, dpi=150)
        plt.close()
        print(f"  📈 Graph saved: {path}")

    def plot_braking_distance_vs_speed(self):
        from config import safe_stopping_distance, kmh_to_ms
        speeds_kmh = np.linspace(10, 80, 100)
        stop_dists = [safe_stopping_distance(kmh_to_ms(s)) for s in speeds_kmh]

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(speeds_kmh, stop_dists, color='#8e44ad',
                linewidth=2.5, label='Required Stopping Distance (AEB)')
        ax.fill_between(speeds_kmh, stop_dists, alpha=0.15, color='#8e44ad')

        for spd in [20, 40, 60]:
            d = safe_stopping_distance(kmh_to_ms(spd))
            ax.scatter([spd], [d], color=COLORS[spd], s=100, zorder=5)
            ax.annotate(f'{spd} km/h\n{d:.1f}m',
                        xy=(spd, d), xytext=(spd + 2, d + 2), fontsize=9,
                        color=COLORS[spd], fontweight='bold')

        ax.axhline(y=OBSTACLE_POSITION_X, color='red', linestyle='--',
                   label=f'Obstacle Position ({OBSTACLE_POSITION_X}m)')
        ax.set_title('Braking Distance vs Vehicle Speed',
                     fontsize=13, fontweight='bold')
        ax.set_xlabel('Speed (km/h)', fontsize=11)
        ax.set_ylabel('Stopping Distance (meters)', fontsize=11)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        path = os.path.join(GRAPH_OUTPUT_DIR, '04_braking_distance_vs_speed.png')
        plt.savefig(path, dpi=150)
        plt.close()
        print(f"  📈 Graph saved: {path}")

    def plot_scenario_comparison(self):
        if not self.results:
            return
        speeds = [r['initial_speed_kmh'] for r in self.results]
        stop_d = [r['theoretical_stop_dist_m'] for r in self.results]
        clearance = [max(r['clearance_m'], 0) for r in self.results]
        prevented = [r['accident_prevented'] for r in self.results]

        x = np.arange(len(speeds))
        width = 0.35
        fig, ax = plt.subplots(figsize=(10, 6))
        bars1 = ax.bar(x - width / 2, stop_d, width, label='Stopping Distance (m)',
                       color=['#2ecc71', '#f39c12', '#e74c3c'], alpha=0.85)
        bars2 = ax.bar(x + width / 2, clearance, width, label='Clearance to Obstacle (m)',
                       color=['#27ae60', '#d68910', '#c0392b'], alpha=0.85)

        for bar, prev in zip(bars1, prevented):
            label_text = '[SAFE]' if prev else '[CRASH]'
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.5,
                    label_text,
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

        ax.set_title('Scenario Comparison: Stopping Distance & Clearance',
                     fontsize=13, fontweight='bold')
        ax.set_xlabel('Initial Speed (km/h)', fontsize=11)
        ax.set_ylabel('Distance (meters)', fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels([f'{s} km/h' for s in speeds])
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        path = os.path.join(GRAPH_OUTPUT_DIR, '05_scenario_comparison.png')
        plt.savefig(path, dpi=150)
        plt.close()
        print(f"  📈 Graph saved: {path}")

    def generate_all(self):
        print("\n  🎨 Generating all simulation graphs...")
        self.plot_speed_vs_time()
        self.plot_acceleration_vs_time()
        self.plot_distance_vs_time()
        self.plot_braking_distance_vs_speed()
        self.plot_scenario_comparison()
        print(f"  ✅ All graphs saved to: {GRAPH_OUTPUT_DIR}")
