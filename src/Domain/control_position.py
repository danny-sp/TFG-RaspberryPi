"""
Manages the control of the vehicle's position using GPS data for the EV charging application.
"""

from typing import Tuple

from src.Persistence.gps_client import GpsPoll
from src.Utils.logger import setup_logger


class ControlPosition:
    """
    ControlPosition is responsible for handling the vehicle's position using GPS data for the EV charging application.
    """

    def __init__(self, gps_client: GpsPoll):
        self.gps_client = gps_client
        self._logger = setup_logger("ControlPosition")

    def get_position(self) -> Tuple[float, float]:
        """Returns the current GPS position as a tuple of (latitude, longitude). If GPS data is not available, returns a default position."""
        default_pos = (0.0, 0.0)  # Default position
        data = self.gps_client.get_data() if self.gps_client else None
        if data:
            latitude = data.get(
                "lat", default_pos[0]
            )  # Default latitude if not available
            longitude = data.get(
                "lon", default_pos[1]
            )  # Default longitude if not available
            return (latitude, longitude)

        return default_pos

    def get_connected_gps(self) -> bool:
        """Returns whether the GPS is connected."""
        return self.gps_client.get_connected() if self.gps_client else False
