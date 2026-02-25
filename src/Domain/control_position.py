from typing import Tuple

from src.Persistance.gps_client import GpsPoll

from src.Utils.logger import setup_logger

class ControlPosition:
    def __init__(self, gps_client: GpsPoll=None):
        self.gps_client = gps_client
        self._logger = setup_logger("ControlPosition")

    def get_position(self) -> Tuple[float, float]:
        default_pos = (39.54505007110555, -4.328554881757664)  # Default position
        data = self.gps_client.get_data() if self.gps_client else None
        if data:
            latitude = data.get('lat', default_pos[0])  # Default latitude if not available
            longitude = data.get('lon', default_pos[1])  # Default longitude if not available
            return (latitude, longitude)

        return default_pos

    def get_connected_gps(self) -> bool:
        return self.gps_client.get_connected() if self.gps_client else False
