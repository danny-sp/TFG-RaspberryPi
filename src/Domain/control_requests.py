import json
from typing import Tuple
import os

from src.Domain.option import Option
from src.Domain.request import Request

from src.Persistance.mqtt_client import MqttService

from src.Utils.logger import setup_logger

class ControlRequests:

    _logger = setup_logger("ControlRequests")
    _plate = os.getenv("VEHICLE_PLATE")

    @classmethod
    def make_request(cls, position: Tuple[float, float], destination: Tuple[float, float]):
        start_coords = position
        end_coords = destination

        cls._logger.info(f"Making request from {start_coords} to {end_coords} with plate {cls._plate}")
        r = Request(plate=cls._plate, position=start_coords, destination=end_coords)

        r_dict = r.to_dict()
        r_json = json.dumps(r_dict)

        MqttService.publish_request(r_json)

        options_str = MqttService.get_response()
        if options_str is None:
            cls._logger.error("Failed to receive options from MQTT response")
            return None
        options_json = json.loads(options_str)

        cls._logger.info(f"Received options: {len(options_json)}")

        options = []
        for option in options_json:
            o = Option.from_dict(option)
            options.append(o)

        return options
