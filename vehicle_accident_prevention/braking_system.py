# ============================================================
# braking_system.py — Automatic Emergency Braking (AEB) System
# Smart Vehicle Accident Prevention Simulation System
# ============================================================

from config import safe_stopping_distance, SAFETY_MARGIN, REACTION_TIME


class AutoEmergencyBraking:
    """
    AEB System — monitors vehicle-to-obstacle distance and
    triggers emergency braking when danger is detected.

    Algorithm:
      1. Calculate required stopping distance at current speed
      2. If distance_to_obstacle <= required_stopping_distance → BRAKE!
      3. Apply maximum deceleration (-μg)
    """

    def __init__(self):
        self.aeb_active = False
        self.trigger_distance = 0.0
        self.trigger_speed_kmh = 0.0
        self.trigger_time = 0.0
        self.warning_issued = False

    def check_and_brake(self, vehicle, obstacle_x: float, current_time: float):
        """
        Main AEB logic — called every simulation timestep.
        Returns: "SAFE", "WARNING", or "BRAKING"
        """
        distance = vehicle.get_distance_to_obstacle(obstacle_x)
        required_stop_dist = safe_stopping_distance(vehicle.speed)

        # --- Stage 1: Early Warning Zone (1.5x safety distance) ---
        if distance <= required_stop_dist * 1.5 and not self.warning_issued:
            self.warning_issued = True
            print(f"  ⚠️  WARNING ZONE at t={current_time:.2f}s | "
                  f"Distance={distance:.1f}m | "
                  f"Required={required_stop_dist:.1f}m")

        # --- Stage 2: Emergency Braking Zone ---
        if distance <= required_stop_dist and not vehicle.braking_applied:
            self.aeb_active = True
            self.trigger_distance = distance
            self.trigger_speed_kmh = vehicle.speed * 3.6
            self.trigger_time = current_time
            vehicle.apply_braking(current_time)
            return "BRAKING"

        if vehicle.braking_applied:
            return "BRAKING"

        if self.warning_issued:
            return "WARNING"

        return "SAFE"

    def get_report(self) -> dict:
        return {
            "aeb_activated": self.aeb_active,
            "trigger_distance_m": round(self.trigger_distance, 2),
            "trigger_speed_kmh": round(self.trigger_speed_kmh, 2),
            "trigger_time_s": round(self.trigger_time, 2),
        }
