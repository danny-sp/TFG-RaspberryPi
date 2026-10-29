"""
Fake route client that builds a route directly from the NMEA file (route.nmea)
instead of calling the remote OSRM server.

Given start and end coordinates it:
  1. Finds the closest point in the NMEA track to *start_coords*.
  2. Finds the closest point in the NMEA track to *end_coords*.
  3. Returns the sub-track between those two points as the route geometry.
  4. Estimates distance (sum of geodesic segments) and duration (distance / avg_speed).

Drop-in replacement for RouteClient — same classmethod signature.
"""

import math

from src.Utils.logger import setup_logger

NMEA_FILE = "route.nmea"
AVG_SPEED_KMH = 60.0   # assumed average speed for duration estimation


def _parse_gprmc_coords(nmea_file: str) -> list[tuple[float, float]]:
    """Returns a list of (lat, lon) decoded from $GPRMC sentences for the continuous leg."""
    coords: list[tuple[float, float]] = []
    try:
        with open(nmea_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                parts = line.split(",")
                if len(parts) < 10 or not parts[0].endswith("GPRMC"):
                    continue
                if parts[2] != "A":
                    continue
                try:
                    lat_raw, lat_dir = parts[3], parts[4]
                    lon_raw, lon_dir = parts[5], parts[6]

                    lat = float(lat_raw[:2]) + float(lat_raw[2:]) / 60.0
                    if lat_dir == "S":
                        lat = -lat

                    lon = float(lon_raw[:3]) + float(lon_raw[3:]) / 60.0
                    if lon_dir == "W":
                        lon = -lon

                    pt = (lat, lon)
                    # Stop if a massive jump occurs (e.g. track resets or repeats)
                    if coords:
                        prev = coords[-1]
                        if abs(pt[0] - prev[0]) > 0.5 or abs(pt[1] - prev[1]) > 0.5:
                            break
                    coords.append(pt)
                except Exception:
                    continue
    except FileNotFoundError:
        pass
    return coords


def _haversine_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Returns the distance in metres between two (lat, lon) points."""
    R = 6_371_000.0
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def _closest_index(track: list[tuple[float, float]], point: tuple[float, float]) -> int:
    """Returns the index of the track point closest to *point*."""
    return min(range(len(track)), key=lambda i: _haversine_m(track[i], point))


def _track_distance_m(track: list[tuple[float, float]]) -> float:
    """Returns the total length of a track in metres."""
    return sum(_haversine_m(track[i], track[i + 1]) for i in range(len(track) - 1))


class FakeRouteClient:
    """
    Offline replacement for RouteClient.
    Reads the pre-recorded NMEA track and slices it between the two
    requested coordinates.
    """

    _logger = setup_logger("FakeRouteClient")
    _track: list[tuple[float, float]] | None = None   # cached once

    @classmethod
    def _get_track(cls) -> list[tuple[float, float]]:
        if cls._track is None:
            cls._track = _parse_gprmc_coords(NMEA_FILE)
            cls._logger.info(
                f"FakeRouteClient loaded {len(cls._track)} track points from '{NMEA_FILE}'"
            )
        return cls._track

    @classmethod
    def get_route_geometry(
        cls,
        start_coords: tuple[float, float],
        end_coords: tuple[float, float],
    ):
        """
        Returns (route_geometry, distance_m, duration_s) from the NMEA track,
        or None if the track is empty.

        Args:
            start_coords: (lat, lon) of the start point.
            end_coords:   (lat, lon) of the end point.
        """
        track = cls._get_track()
        if not track:
            cls._logger.error("NMEA track is empty — cannot build fake route.")
            return None

        i_start = _closest_index(track, start_coords)
        i_end = _closest_index(track, end_coords)

        # Slice along track in the correct direction
        if i_start <= i_end:
            sub_track = list(track[i_start : i_end + 1])
        else:
            sub_track = list(reversed(track[i_end : i_start + 1]))

        if not sub_track:
            sub_track = [start_coords, end_coords]
        else:
            # Connect seamlessly to start and end markers without gaps
            if _haversine_m(start_coords, sub_track[0]) > 1.0:
                sub_track.insert(0, start_coords)
            if _haversine_m(end_coords, sub_track[-1]) > 1.0:
                sub_track.append(end_coords)

        distance_m = _track_distance_m(sub_track)
        duration_s = (distance_m / 1000.0) / AVG_SPEED_KMH * 3600.0

        cls._logger.debug(
            f"FakeRoute: indices [{i_start}…{i_end}], "
            f"{len(sub_track)} pts, {distance_m/1000:.2f} km, {duration_s/60:.1f} min"
        )

        return sub_track, distance_m, duration_s

