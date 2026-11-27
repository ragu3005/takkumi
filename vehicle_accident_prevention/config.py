# ============================================================
# config.py — Project Configuration File
# Smart Vehicle Accident Prevention Simulation System
# ============================================================

# --- Simulation Settings ---
SIMULATION_TIMESTEP = 0.01       # 10ms per step (100 Hz)
SIMULATION_DURATION = 30.0       # Total simulation time in seconds

# --- Vehicle Initial Settings ---
VEHICLE_MASS = 1500.0            # kg (typical sedan)
VEHICLE_START_X = 0.0            # meters
VEHICLE_START_Y = 0.5            # meters (height above ground)
VEHICLE_START_Z = 0.0            # meters

# --- Speed Test Scenarios (km/h → m/s) ---
TEST_SPEEDS_KMH = [20, 40, 60]
def kmh_to_ms(kmh): return kmh / 3.6

# --- Road Settings ---
ROAD_LENGTH = 300.0              # meters
ROAD_WIDTH = 10.0                # meters

# --- Obstacle Settings ---
OBSTACLE_POSITION_X = 80.0      # meters from start
OBSTACLE_MASS = 500.0            # kg
OBSTACLE_SIZE = (2.0, 1.5, 1.0) # width, height, depth

# --- Braking System Settings ---
REACTION_TIME = 0.8              # seconds (human reaction approximation)
FRICTION_COEFFICIENT = 0.7       # dry road friction
GRAVITY = 9.81                   # m/s²
SAFETY_MARGIN = 5.0              # extra safety buffer (meters)

# --- Braking Distance Formula: d = v²/(2μg) ---
def safe_stopping_distance(speed_ms):
    braking_dist = (speed_ms ** 2) / (2 * FRICTION_COEFFICIENT * GRAVITY)
    reaction_dist = speed_ms * REACTION_TIME
    return braking_dist + reaction_dist + SAFETY_MARGIN

# --- Output Paths ---
DATA_OUTPUT_DIR = r"C:\Simulation System\vehicle_accident_prevention\data"
GRAPH_OUTPUT_DIR = r"C:\Simulation System\vehicle_accident_prevention\graphs"
LOG_OUTPUT_DIR  = r"C:\Simulation System\vehicle_accident_prevention\logs"

# --- Collision Detection ---
COLLISION_THRESHOLD = 1.5        # meters (vehicle considered collided if closer)
