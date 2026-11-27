# ============================================================
# vehicle_model.py — Vehicle Physics Model
# Smart Vehicle Accident Prevention Simulation System
# ============================================================

import numpy as np
from config import (VEHICLE_MASS, FRICTION_COEFFICIENT, GRAVITY,
                    REACTION_TIME, SIMULATION_TIMESTEP, kmh_to_ms)


class VehicleModel:
    """
    Physics-based vehicle model using kinematic equations.
    Simulates position, velocity, acceleration, and braking.
    """

    def __init__(self, initial_speed_kmh: float, start_x: float = 0.0):
        self.mass = VEHICLE_MASS                        # kg
        self.speed = kmh_to_ms(initial_speed_kmh)      # m/s (current)
        self.initial_speed = self.speed                 # m/s (saved)
        self.initial_speed_kmh = initial_speed_kmh
        self.position_x = start_x                      # meters along road
        self.acceleration = 0.0                         # m/s²
        self.braking_applied = False
        self.brake_start_time = None
        self.collision_occurred = False
        self.stopped = False
        self.time_elapsed = 0.0

        # Data recording lists
        self.time_log = []
        self.speed_log = []
        self.position_log = []
        self.accel_log = []
        self.brake_log = []

    def apply_braking(self, current_time: float):
        """Apply maximum emergency braking force."""
        if not self.braking_applied:
            self.braking_applied = True
            self.brake_start_time = current_time
            print(f"  🚨 EMERGENCY BRAKING at t={current_time:.2f}s | "
                  f"Speed={self.speed * 3.6:.1f} km/h | Pos={self.position_x:.1f}m")

        # Braking deceleration: a = -μg
        self.acceleration = -FRICTION_COEFFICIENT * GRAVITY  # ≈ -6.87 m/s²

    def update(self, dt: float):
        """
        Update vehicle state for one timestep.
        Uses kinematic equations:
          v = v0 + a*dt
          x = x0 + v*dt
        """
        if self.stopped:
            self.acceleration = 0.0
            self._record(dt)
            return

        # Update speed
        self.speed += self.acceleration * dt

        # Cannot go negative speed (vehicle doesn't reverse from braking)
        if self.speed <= 0.0:
            self.speed = 0.0
            self.acceleration = 0.0
            self.stopped = True
            print(f"  🛑 Vehicle STOPPED at position={self.position_x:.2f}m "
                  f"at t={self.time_elapsed:.2f}s")

        # Update position
        self.position_x += self.speed * dt
        self.time_elapsed += dt
        self._record(dt)

    def _record(self, dt):
        """Save current state to logs."""
        self.time_log.append(self.time_elapsed)
        self.speed_log.append(self.speed * 3.6)          # Store in km/h
        self.position_log.append(self.position_x)
        self.accel_log.append(self.acceleration)
        self.brake_log.append(1 if self.braking_applied else 0)

    def get_distance_to_obstacle(self, obstacle_x: float) -> float:
        """Calculate distance from vehicle front to obstacle."""
        return obstacle_x - self.position_x

    def get_state(self) -> dict:
        """Return current vehicle state as dictionary."""
        return {
            "time": self.time_elapsed,
            "position_m": self.position_x,
            "speed_kmh": self.speed * 3.6,
            "speed_ms": self.speed,
            "acceleration": self.acceleration,
            "braking": self.braking_applied,
            "stopped": self.stopped,
            "collision": self.collision_occurred,
        }

    def stopping_distance_theoretical(self) -> float:
        """Calculate theoretical stopping distance from initial speed."""
        v = self.initial_speed
        d_brake = (v ** 2) / (2 * FRICTION_COEFFICIENT * GRAVITY)
        d_react = v * REACTION_TIME
        return d_brake + d_react
