import json
from typing import Tuple
import os

from src.Domain.request import Request

from src.Persistance.mqtt_client import MqttService

from src.Utils.logger import setup_logger

class ControlRequests:

    _logger = setup_logger("ControlRequests")
    _plate = os.getenv("VEHICLE_PLATE")

    @classmethod
    def make_request(cls, position: Tuple[float, float], destination: str):
        start_coords = position
        end_destination = destination

        cls._logger.info(f"Making request from {start_coords} to {end_destination} with plate {cls._plate}")
        r = Request(plate=cls._plate, destination=end_destination)

        r_dict = r.to_dict()
        r_json = json.dumps(r_dict)

        MqttService.publish_request(r_json)


