import requests
import polyline

from src.Utils.logger import setup_logger

def get_route_geometry(start_coords, end_coords):
    logger = setup_logger("RouteClient")

    url = f"http://server:5000/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if data["code"] != "Ok":
            logger.error(f"Error with OSRM: {data['code']}")
            return None

        encoded_geometry = data['routes'][0]['geometry']
        return polyline.decode(encoded_geometry)

    except requests.RequestException as e:
        logger.error(f"Connection error: {e}")
        return None
