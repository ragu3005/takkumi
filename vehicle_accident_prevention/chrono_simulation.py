# ============================================================
# chrono_simulation.py — Project Chrono Physics Simulation
# Smart Vehicle Accident Prevention Simulation System
#
# Uses official Project Chrono Python bindings (pychrono.core)
# for 3D multi-body dynamics, contact, and collision detection.
# ============================================================

import sys, os

CHRONO_AVAILABLE = False
try:
    import pychrono.core as chrono
    CHRONO_AVAILABLE = True
    print("  ✅ Project Chrono Python bindings (pychrono.core) loaded successfully!")
except ImportError:
    print("  ⚠️  pychrono not found — using kinematic physics engine.")

from config import (SIMULATION_TIMESTEP, OBSTACLE_POSITION_X,
                    VEHICLE_MASS, FRICTION_COEFFICIENT, GRAVITY)


class ChronoVehicleSimulation:
    """
    Project Chrono 10 3D physical system for vehicle accident simulation.
    Features:
      - 3D Multi-body ground and vehicle
      - Cruise control at target speed
      - Automatic Emergency Braking (AEB)
      - Collision detection with obstacle
    """

    def __init__(self, speed_kmh: float):
        if not CHRONO_AVAILABLE:
            raise RuntimeError("pychrono not installed.")

        self.speed_kmh = speed_kmh
        self.speed_ms = speed_kmh / 3.6

        # --- Create Chrono Physical System ---
        self.system = chrono.ChSystemNSC()
        self.system.SetGravitationalAcceleration(chrono.ChVector3d(0, -GRAVITY, 0))
        self.system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

        # --- Create Ground Body (Road) ---
        ground_mat = chrono.ChContactMaterialNSC()
        ground_mat.SetFriction(FRICTION_COEFFICIENT)
        ground_mat.SetRestitution(0.1)

        self.ground = chrono.ChBodyEasyBox(300.0, 0.2, 10.0, 1000.0, True, True, ground_mat)
        self.ground.SetPos(chrono.ChVector3d(150.0, -0.1, 0.0))
        self.ground.SetFixed(True)
        if self.ground.GetVisualModel() and self.ground.GetVisualModel().GetNumShapes() > 0:
            self.ground.GetVisualModel().GetShape(0).SetColor(chrono.ChColor(0.2, 0.2, 0.2))
        self.system.Add(self.ground)

        # --- Create Vehicle Body ---
        vehicle_mat = chrono.ChContactMaterialNSC()
        vehicle_mat.SetFriction(FRICTION_COEFFICIENT)

        density = VEHICLE_MASS / (4.5 * 1.5 * 2.0)
        self.vehicle_body = chrono.ChBodyEasyBox(4.5, 1.5, 2.0, density, True, True, vehicle_mat)
        self.vehicle_body.SetPos(chrono.ChVector3d(0.0, 0.75, 0.0))
        self.vehicle_body.SetLinVel(chrono.ChVector3d(self.speed_ms, 0.0, 0.0))
        if self.vehicle_body.GetVisualModel() and self.vehicle_body.GetVisualModel().GetNumShapes() > 0:
            self.vehicle_body.GetVisualModel().GetShape(0).SetColor(chrono.ChColor(0.1, 0.4, 0.8))
        self.system.Add(self.vehicle_body)

        # --- Create Obstacle Body ---
        obstacle_mat = chrono.ChContactMaterialNSC()
        obstacle_mat.SetFriction(0.6)

        self.obstacle_body = chrono.ChBodyEasyBox(2.0, 1.5, 1.0, 500.0, True, True, obstacle_mat)
        self.obstacle_body.SetPos(chrono.ChVector3d(OBSTACLE_POSITION_X, 0.75, 0.0))
        self.obstacle_body.SetFixed(True)
        if self.obstacle_body.GetVisualModel() and self.obstacle_body.GetVisualModel().GetNumShapes() > 0:
            self.obstacle_body.GetVisualModel().GetShape(0).SetColor(chrono.ChColor(0.9, 0.1, 0.1))
        self.system.Add(self.obstacle_body)

        # --- Data logs ---
        self.time_log = []
        self.pos_log = []
        self.speed_log = []
        self.accel_log = []
        self.brake_log = []
        self.braking = False
        self.stopped = False

        print(f"  🏎️  Project Chrono vehicle created | Cruise Speed: {speed_kmh} km/h ({self.speed_ms:.2f} m/s)")

    def step(self, dt: float, t: float, aeb_active: bool):
        vel = self.vehicle_body.GetLinVel()
        vx = vel.x

        if aeb_active and not self.stopped:
            if not self.braking:
                self.braking = True
                print(f"  🚨 Chrono AEB Emergency Braking triggered at t={t:.2f}s | Pos={self.vehicle_body.GetPos().x:.2f}m")

            # Deceleration under braking: a = -μg
            decel = FRICTION_COEFFICIENT * GRAVITY
            new_vx = vx - decel * dt
            if new_vx <= 0.01:
                new_vx = 0.0
                self.stopped = True
                print(f"  🛑 Project Chrono vehicle stopped safely at position={self.vehicle_body.GetPos().x:.2f}m")
            self.vehicle_body.SetLinVel(chrono.ChVector3d(new_vx, vel.y, vel.z))
            current_accel = -decel if not self.stopped else 0.0
        elif not self.stopped:
            # Cruise Control: Maintain set vehicle speed
            self.vehicle_body.SetLinVel(chrono.ChVector3d(self.speed_ms, vel.y, vel.z))
            current_accel = 0.0
        else:
            current_accel = 0.0

        # Step Chrono multi-body dynamic physics
        self.system.DoStepDynamics(dt)

        pos = self.vehicle_body.GetPos()
        curr_vel = self.vehicle_body.GetLinVel()
        spd = max(curr_vel.x, 0.0)

        self.time_log.append(t)
        self.pos_log.append(pos.x)
        self.speed_log.append(spd * 3.6)
        self.accel_log.append(current_accel)
        self.brake_log.append(1 if self.braking else 0)

        return pos.x, spd

    def get_vehicle_position(self) -> float:
        return self.vehicle_body.GetPos().x

    def get_vehicle_speed(self) -> float:
        return max(self.vehicle_body.GetLinVel().x, 0.0)


def run_chrono_scenario(speed_kmh: int) -> dict:
    from braking_system import AutoEmergencyBraking

    sim = ChronoVehicleSimulation(speed_kmh)
    aeb = AutoEmergencyBraking()

    class ChronoVehicleAdapter:
        def __init__(self, chrono_sim):
            self.cs = chrono_sim
            self.initial_speed = chrono_sim.speed_ms
            self.initial_speed_kmh = chrono_sim.speed_kmh
            self.braking_applied = False
            self.collision_occurred = False
            self.stopped = False
            self.time_log = chrono_sim.time_log
            self.speed_log = chrono_sim.speed_log
            self.position_log = chrono_sim.pos_log
            self.accel_log = chrono_sim.accel_log
            self.brake_log = chrono_sim.brake_log
            self.brake_start_time = None

        @property
        def speed(self):
            return self.cs.get_vehicle_speed()

        @property
        def position_x(self):
            return self.cs.get_vehicle_position()

        def get_distance_to_obstacle(self, obs_x):
            return obs_x - self.position_x

        def apply_braking(self, t):
            self.braking_applied = True
            if self.brake_start_time is None:
                self.brake_start_time = t

        def stopping_distance_theoretical(self):
            from config import REACTION_TIME
            v = self.initial_speed
            return (v**2) / (2 * FRICTION_COEFFICIENT * GRAVITY) + v * REACTION_TIME

    adapter = ChronoVehicleAdapter(sim)
    dt = SIMULATION_TIMESTEP
    t = 0.0
    collision = False

    while t <= 30.0:
        pos_x = sim.get_vehicle_position()
        spd = sim.get_vehicle_speed()

        # AEB monitoring
        aeb.check_and_brake(adapter, OBSTACLE_POSITION_X, t)

        # Collision detection (Obstacle front is at OBSTACLE_POSITION_X - 1.0)
        dist = OBSTACLE_POSITION_X - pos_x
        if dist <= 1.5 and spd > 0.1:
            collision = True
            adapter.collision_occurred = True
            print(f"  💥 CHRONO COLLISION at t={t:.2f}s! Impact Speed={spd*3.6:.1f} km/h")
            break

        # Step Chrono dynamics
        pos_x, spd = sim.step(dt, t, adapter.braking_applied)

        if spd <= 0.01 and adapter.braking_applied:
            adapter.stopped = True
            break

        t += dt

    final_pos = sim.get_vehicle_position()
    clearance = OBSTACLE_POSITION_X - final_pos

    return {
        "initial_speed_kmh": speed_kmh,
        "vehicle_final_position_m": round(final_pos, 2),
        "clearance_m": round(clearance, 2),
        "collision_occurred": collision,
        "accident_prevented": not collision,
        "aeb_activated": adapter.braking_applied,
        "vehicle": adapter,
        "aeb": aeb,
    }
