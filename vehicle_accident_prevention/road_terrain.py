# ============================================================
# road_terrain.py — Road and Environment Model
# Smart Vehicle Accident Prevention Simulation System
# ============================================================

from config import ROAD_LENGTH, ROAD_WIDTH


class RoadTerrain:
    """
    Simulates a straight flat road for the vehicle to travel on.
    Defines road boundaries, lanes, and terrain properties.
    """

    def __init__(self):
        self.length = ROAD_LENGTH           # meters
        self.width = ROAD_WIDTH             # meters
        self.friction = 0.7                 # dry asphalt coefficient
        self.surface = "dry_asphalt"
        self.lanes = 2
        self.lane_width = self.width / self.lanes  # 5 meters each

        print(f"  🛣️  Road created: {self.length}m long x {self.width}m wide")
        print(f"  🛣️  Surface: {self.surface} | Friction: {self.friction}")

    def is_on_road(self, position_x: float) -> bool:
        """Check if the vehicle is still within road boundaries."""
        return 0.0 <= position_x <= self.length

    def get_lane(self, position_z: float) -> int:
        """Return which lane the vehicle is in (1 or 2)."""
        if 0 <= position_z < self.lane_width:
            return 1
        return 2

    def get_road_info(self) -> dict:
        """Return road configuration summary."""
        return {
            "length_m": self.length,
            "width_m": self.width,
            "surface": self.surface,
            "friction_coeff": self.friction,
            "lanes": self.lanes,
        }
