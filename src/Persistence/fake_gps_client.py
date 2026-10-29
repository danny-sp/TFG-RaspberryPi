"""
Fake GPS client that replays positions from a NMEA file (route.nmea)
instead of connecting to real GPS hardware via gpsd.

Drop-in replacement for GpsPoll — same public interface.
"""

import threading
import time

from src.Utils.logger import setup_logger

NMEA_FILE = "route.nmea"


def _parse_gprmc(sentence: str) -> dict | None:
    """
    Parses a $GPRMC sentence and returns a dict with lat/lon/time,
    or None if the sentence is invalid or has no fix.

    $GPRMC,HHMMSS.ss,A,LLLL.LL,a,YYYYY.YY,a,x.x,x.x,DDMMYY,x.x,a*hh
    """
    try:
        parts = sentence.strip().split(",")
        if len(parts) < 10:
            return None
        if not parts[0].endswith("GPRMC"):
            return None
        if parts[2] != "A":  # 'A' = active / valid fix
            return None

        raw_time = parts[1]  # HHMMSS.ss
        lat_raw = parts[3]   # LLLL.LL
        lat_dir = parts[4]   # N/S
        lon_raw = parts[5]   # YYYYY.YY
        lon_dir = parts[6]   # E/W

        # Convert DDMM.MMMM → decimal degrees
        lat_deg = float(lat_raw[:2])
        lat_min = float(lat_raw[2:])
        lat = lat_deg + lat_min / 60.0
        if lat_dir == "S":
            lat = -lat

        lon_deg = float(lon_raw[:3])
        lon_min = float(lon_raw[3:])
        lon = lon_deg + lon_min / 60.0
        if lon_dir == "W":
            lon = -lon

        return {
            "lat": lat,
            "lon": lon,
            "alt": None,
            "time": raw_time,
        }
    except Exception:
        return None


class FakeGpsPoll(threading.Thread):
    """
    Thread that replays NMEA positions from *route.nmea* at the cadence
    of the real sentences (every ~2 seconds per group) and exposes the
    same interface as GpsPoll.
    """

    def __init__(self, nmea_file: str = NMEA_FILE, interval: float = 1.0):
        super().__init__(daemon=True)
        self._nmea_file = nmea_file
        self._interval = interval   # seconds between position updates
        self.last_value: dict | None = None
        self.running = True
        self.connected = False
        self._lock = threading.Lock()
        self._logger = setup_logger("FakeGpsPoll")
        self._logger.info(f"FakeGpsPoll initialised — reading from '{nmea_file}'")

    # ------------------------------------------------------------------
    # Thread body
    # ------------------------------------------------------------------

    def run(self):
        while self.running:
            positions = self._load_positions()
            if not positions:
                self._logger.error(
                    f"No valid GPRMC sentences found in '{self._nmea_file}'. "
                    "Retrying in 5 s…"
                )
                time.sleep(5)
                continue

            self._logger.info(
                f"Replaying {len(positions)} GPS positions from '{self._nmea_file}'"
            )
            for pos in positions:
                if not self.running:
                    return
                with self._lock:
                    self.last_value = pos
                    self.connected = True
                self._logger.debug(f"FakeGPS → lat={pos['lat']:.6f}, lon={pos['lon']:.6f}")
                time.sleep(self._interval)

            self._logger.info("Route finished — looping back to the start.")

    def _load_positions(self) -> list[dict]:
        """Reads the NMEA file and returns a list of position dicts for the continuous leg."""
        positions = []
        try:
            with open(self._nmea_file, "r", encoding="utf-8") as f:
                for line in f:
                    pos = _parse_gprmc(line)
                    if pos is not None:
                        # Stop if a massive jump occurs (e.g. log restarts/repeats)
                        if positions:
                            prev = (positions[-1]["lat"], positions[-1]["lon"])
                            curr = (pos["lat"], pos["lon"])
                            if abs(curr[0] - prev[0]) > 0.5 or abs(curr[1] - prev[1]) > 0.5:
                                break
                        positions.append(pos)
        except FileNotFoundError:
            self._logger.error(f"NMEA file not found: '{self._nmea_file}'")
        except Exception as e:
            self._logger.error(f"Error reading NMEA file: {e}")
        return positions

    # ------------------------------------------------------------------
    # Public interface — identical to GpsPoll
    # ------------------------------------------------------------------

    def get_data(self) -> dict | None:
        """Returns the last known GPS position."""
        with self._lock:
            return self.last_value

    def get_connected(self) -> bool:
        """Returns whether the fake GPS has produced at least one position."""
        with self._lock:
            return self.connected

    def stop(self):
        """Stops the thread cleanly."""
        self.running = False

