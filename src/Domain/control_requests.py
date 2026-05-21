"""
ControlRequests class responsible for creating and sending requests to the backend via MQTT, and processing the received
options.
"""

import json
import os
from typing import Tuple

from src.Domain.option import Option
from src.Domain.request import Request
from src.Persistence.mqtt_client import MqttService
from src.Utils.logger import setup_logger


class ControlRequests:
    """
    ControlRequests class responsible for creating and sending requests to the backend via MQTT, and processing the received options.
    """

    _logger = setup_logger("ControlRequests")
    _plate = os.getenv("VEHICLE_PLATE", "1234 BCD")

    @classmethod
    def make_request(
        cls, position: Tuple[float, float], destination: Tuple[float, float]
    ) -> list[Option]:
        """
        Creates and sends a request to the backend via MQTT, and processes the received options.

        Args:
            position (Tuple[float, float]): The current GPS position as a tuple of (latitude, longitude).
            destination (Tuple[float, float]): The destination coordinates as a tuple of (latitude, longitude).

        Returns:
            list[Option]: A list of Option objects representing the received options from the backend.
        """

        start_coords = position
        end_coords = destination

        cls._logger.info(
            f"Making request from {start_coords} to {end_coords} with plate {cls._plate}"
        )
        # TODO: Fixed current percent for testing.
        r = Request(
            plate=cls._plate,
            current_percent=60.0,
            position=start_coords,
            destination=end_coords,
        )

        r_dict = r.to_dict()
        r_json = json.dumps(r_dict)

        MqttService.publish_request(r_json)

        options_str = MqttService.get_response()
        if options_str is None:
            cls._logger.error("Failed to receive options from MQTT response")
            return []
        options_json = json.loads(options_str)

        cls._logger.info(f"Received options: {len(options_json)}")

        options = []
        for option in options_json:
            o = Option.from_dict(option)
            options.append(o)

        return options
