"""
Fake MQTT service that returns hard-coded charging options without
connecting to any external broker.

Drop-in replacement for MqttService — same classmethods:
  · publish_request(request_json)
  · get_response(timeout) → str | None
  · setup_message_callback()
"""

import json
import math
import threading
import time
import uuid
from datetime import datetime, timedelta

from src.Utils.logger import setup_logger

# ---------------------------------------------------------------------------
# Fake options catalogue — estaciones en la ruta Ciudad Real → Madrid (A-4)
# ---------------------------------------------------------------------------

_FAKE_OPTIONS: list[dict] = [
    {
        "request_id": "",          # filled in at runtime
        "charging_station": {
            "id": 1,
            "name": "Iberdrola Madridejos",
            "location": [39.4721, -3.5330],   # Madridejos, A-4 km ~130
            "operator": "Iberdrola",
        },
        "price": 8.40,
        "kw_speed": 50.0,
        "start_time": "",          # filled in at runtime
        "end_time": "",            # filled in at runtime
        "charging_hours": 0.5,
        "route_hours": 0.8,
        "delay_hours": 0.1,
        "services_nearby": ["CAFE", "RESTAURANT"],
    },
    {
        "request_id": "",
        "charging_station": {
            "id": 2,
            "name": "Repsol Ocaña",
            "location": [39.9568, -3.4938],   # Ocaña, A-4 km ~70
            "operator": "Repsol",
        },
        "price": 11.20,
        "kw_speed": 100.0,
        "start_time": "",
        "end_time": "",
        "charging_hours": 0.3,
        "route_hours": 1.3,
        "delay_hours": 0.05,
        "services_nearby": ["SUPERMARKET", "ATM"],
    },
    {
        "request_id": "",
        "charging_station": {
            "id": 3,
            "name": "Endesa Valdemoro",
            "location": [40.1912, -3.6741],   # Valdemoro, A-4 km ~25
            "operator": "Endesa",
        },
        "price": 6.90,
        "kw_speed": 22.0,
        "start_time": "",
        "end_time": "",
        "charging_hours": 1.0,
        "route_hours": 1.8,
        "delay_hours": 0.2,
        "services_nearby": ["MOTEL", "CAFE", "PHARMACY"],
    },
]

_FAKE_DELAY_S: float = 1.0   # simulated network delay in seconds


def _haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Returns distance in km between two (lat, lon) points."""
    R = 6371.0
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def _build_options(
    request_id: str, current_pos: tuple[float, float] | None = None
) -> list[dict]:
    """Clones the template list and fills in runtime fields."""
    now = datetime.now()
    result = []
    for tpl in _FAKE_OPTIONS:
        opt = json.loads(json.dumps(tpl))   # deep-copy via JSON round-trip
        opt["request_id"] = request_id
        
        # Calculate dynamic route_hours if position is provided
        if current_pos:
            st_loc = tuple(opt["charging_station"]["location"])
            d_km = _haversine_km(current_pos, st_loc)
            opt["route_hours"] = max(0.1, round(d_km / 80.0, 2))

        start = now + timedelta(hours=opt["route_hours"])
        end = start + timedelta(hours=opt["charging_hours"])
        opt["start_time"] = start.isoformat()
        opt["end_time"] = end.isoformat()
        result.append(opt)
    return result


class FakeMqttService:
    """
    Simulates the MQTT round-trip locally:
      · publish_request() stores the last request_id and position.
      · get_response() waits _FAKE_DELAY_S seconds and returns
        a JSON-encoded list of fake options.
    """

    _logger = setup_logger("FakeMqttService")
    _last_request_id: str = ""
    _last_position: tuple[float, float] | None = None
    _message_event = threading.Event()

    @classmethod
    def publish_request(cls, request_json: str):
        """Stores the request and signals that a response is ready."""
        cls._logger.info(f"[FAKE MQTT] publish_request: {request_json[:120]}…")
        try:
            data = json.loads(request_json)
            cls._last_request_id = data.get("uuid", str(uuid.uuid4()))
            lat = data.get("latitude")
            lon = data.get("longitude")
            if lat is not None and lon is not None:
                cls._last_position = (float(lat), float(lon))
        except Exception:
            cls._last_request_id = str(uuid.uuid4())
            cls._last_position = None

        # Simulate async broker processing in a background thread
        def _delayed_signal():
            time.sleep(_FAKE_DELAY_S)
            cls._message_event.set()

        threading.Thread(target=_delayed_signal, daemon=True).start()

    @classmethod
    def get_response(cls, timeout: int = 60) -> str | None:
        """Waits for the fake broker and returns a JSON options list."""
        cls._logger.info(
            f"[FAKE MQTT] Waiting for fake response (delay≈{_FAKE_DELAY_S} s)…"
        )
        cls._message_event.clear()

        if cls._message_event.wait(timeout):
            options = _build_options(cls._last_request_id, cls._last_position)
            response = json.dumps(options)
            cls._logger.info(
                f"[FAKE MQTT] Returning {len(options)} fake options."
            )
            return response

        cls._logger.warning("[FAKE MQTT] Timeout waiting for fake response.")
        return None

    @classmethod
    def setup_message_callback(cls):
        """No-op — fake service does not need an MQTT loop."""
        cls._logger.debug("[FAKE MQTT] setup_message_callback called (no-op).")

