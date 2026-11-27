# ============================================================
# collision_detection.py — Collision Detection System
# Smart Vehicle Accident Prevention Simulation System
# ============================================================

from config import COLLISION_THRESHOLD
import csv, os
from datetime import datetime
from config import LOG_OUTPUT_DIR


class CollisionDetector:
    """
    Checks every timestep whether the vehicle has reached
    or passed the obstacle position (collision event).
    """

    def __init__(self, obstacle_x: float):
        self.obstacle_x = obstacle_x
        self.collision_threshold = COLLISION_THRESHOLD
        self.collision_events = []

    def check_collision(self, vehicle, current_time: float) -> bool:
        """
        Returns True if vehicle has collided with obstacle.
        Collision = vehicle position >= obstacle_x - threshold
        """
        if vehicle.collision_occurred:
            return True

        distance = vehicle.get_distance_to_obstacle(self.obstacle_x)

        if distance <= self.collision_threshold and not vehicle.stopped:
            vehicle.collision_occurred = True
            impact_speed = vehicle.speed * 3.6
            event = {
                "time_s": round(current_time, 3),
                "position_m": round(vehicle.position_x, 2),
                "impact_speed_kmh": round(impact_speed, 2),
                "distance_at_impact_m": round(distance, 3),
                "initial_speed_kmh": vehicle.initial_speed_kmh,
            }
            self.collision_events.append(event)
            print(f"\n  💥 COLLISION DETECTED at t={current_time:.2f}s!")
            print(f"     Impact Speed: {impact_speed:.1f} km/h")
            print(f"     Position: {vehicle.position_x:.2f}m")
            return True

        return False

    def save_collision_log(self, speed_label: str):
        """Save collision events to CSV."""
        if not self.collision_events:
            return
        os.makedirs(LOG_OUTPUT_DIR, exist_ok=True)
        filename = os.path.join(LOG_OUTPUT_DIR, f"collision_log_{speed_label}kmh.csv")
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.collision_events[0].keys())
            writer.writeheader()
            writer.writerows(self.collision_events)
        print(f"  📄 Collision log saved: {filename}")

    def get_summary(self) -> dict:
        return {
            "total_collisions": len(self.collision_events),
            "events": self.collision_events,
        }
