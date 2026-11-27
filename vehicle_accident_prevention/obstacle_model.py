# ============================================================
# obstacle_model.py — Obstacle Model
# Smart Vehicle Accident Prevention Simulation System
# ============================================================

from config import OBSTACLE_POSITION_X, OBSTACLE_MASS, OBSTACLE_SIZE


class ObstacleModel:
    """
    Represents a static obstacle (e.g., broken-down car, debris)
    placed on the road in front of the vehicle.
    """

    def __init__(self, position_x: float = OBSTACLE_POSITION_X):
        self.position_x = position_x          # meters from road start
        self.mass = OBSTACLE_MASS             # kg
        self.width, self.height, self.depth = OBSTACLE_SIZE
        self.is_active = True
        self.obstacle_type = "static_vehicle"

        print(f"  🚧 Obstacle placed at: {self.position_x}m from start")
        print(f"  🚧 Obstacle size: {self.width}m x {self.height}m x {self.depth}m")

    def get_front_edge(self) -> float:
        """Return the front-facing edge of the obstacle."""
        return self.position_x - (self.depth / 2.0)

    def get_back_edge(self) -> float:
        """Return the rear-facing edge of the obstacle."""
        return self.position_x + (self.depth / 2.0)

    def get_info(self) -> dict:
        return {
            "position_m": self.position_x,
            "type": self.obstacle_type,
            "width_m": self.width,
            "height_m": self.height,
            "depth_m": self.depth,
            "active": self.is_active,
        }
