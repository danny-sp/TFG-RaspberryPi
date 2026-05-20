"""
Manages route requests and distance calculations for the EV charging application.
"""

from typing import Tuple

from geopy.distance import geodesic  # type: ignore

from src.Persistance.route_client import RouteClient
from src.Utils.constants import Destinations
from src.Utils.logger import setup_logger


class ControlRoute:
    """
    ControlRoute is responsible for handling route requests and distance calculations for the EV charging application.
    """

    _logger = setup_logger("ControlRoute")

    @classmethod
    def get_route_str(cls, coords: Tuple[float, float], destination: str):
        """
        Fetches the route geometry from the current coordinates to the specified destination.

        Args:
            coords (Tuple[float, float]): The current GPS coordinates (latitude, longitude).
            destination (str): The name of the destination ("BILBAO" or "MADRID").
        Returns:
            The route geometry if found, otherwise None.
        """

        start_coords = coords

        try:
            end_coords = Destinations[destination].value
        except KeyError:
            cls._logger.warning(f"Unknown destination '{destination}' requested")
            return None

        cls._logger.debug(
            f"Fetching route from {start_coords} to {end_coords} for destination '{destination}'"
        )
        response = RouteClient.get_route_geometry(start_coords, end_coords)

        if response is None:
            cls._logger.warning(f"No route found for destination '{destination}'")
            return None

        return response

    @classmethod
    def get_route_coords(
        cls, coords: Tuple[float, float], destination: Tuple[float, float]
    ) -> Tuple | None:
        """
        Fetches the route geometry from the current coordinates to the specified destination coordinates.

        Args:
            coords (Tuple[float, float]): The current GPS coordinates (latitude, longitude).
            destination (Tuple[float, float]): The destination GPS coordinates (latitude, longitude).

        Returns:
            The route geometry if found, otherwise None.
        """
        start_coords = coords
        end_coords = destination

        cls._logger.debug(
            f"Fetching route from {start_coords} to {end_coords} for custom coordinates"
        )
        response = RouteClient.get_route_geometry(start_coords, end_coords)

        if response is None:
            cls._logger.warning(f"No route found for custom coordinates {destination}")
            return None

        return response

    @classmethod
    def get_distance_coords(
        cls, coords: Tuple[float, float], destination: Tuple[float, float]
    ) -> float:
        """
        Fetches the distance from the current coordinates to the specified destination coordinates. If no route is found, calculates the geodesic distance.

        Args:
            coords (Tuple[float, float]): The current GPS coordinates (latitude, longitude).
            destination (Tuple[float, float]): The destination GPS coordinates (latitude, longitude).

        Returns:
            The distance in kilometers from the current coordinates to the destination.
        """

        start_coords = coords
        end_coords = destination

        cls._logger.debug(
            f"Fetching distance from {start_coords} to {end_coords} for custom coordinates"
        )
        response = RouteClient.get_route_geometry(start_coords, end_coords)

        if response is None:
            cls._logger.warning(f"No route found for custom coordinates {destination}")
            distance = geodesic(start_coords, end_coords).kilometers
        else:
            _, distance, _ = response
            distance /= 1000

        return distance
