"""
Module responsible for interfacing with the GPS hardware and providing location data to the rest of the application.
"""

import threading
import time

import gpsd  # type: ignore

from src.Utils.logger import setup_logger


class GpsPoll(threading.Thread):
    """
    Thread that continuously polls GPS data and stores the last known position and connection status.
    """

    def __init__(self):
        super().__init__()
        gpsd.connect()
        self.last_value = None
        self.running = True
        self.connected = False
        self._lock = threading.Lock()  # Avoids race conditions
        self._logger = setup_logger("gps_client")

    def run(self):
        """
        Updates the last known GPS position
        """
        try:
            while self.running:
                packet = gpsd.get_current()
                if packet.mode >= 2:  # 2D fix or better
                    with self._lock:
                        self.connected = True
                        self.last_value = {
                            "lat": packet.lat,
                            "lon": packet.lon,
                            "alt": packet.alt if packet.mode >= 3 else None,
                            "time": packet.time,
                        }
                else:
                    with self._lock:
                        self.connected = False
                time.sleep(1)  # Poll every second
        except Exception as e:
            self._logger.error(f"Error in GPS thread: {e}")
            self.connected = False

    def get_data(self) -> dict:
        """
        Returns the last known GPS position.

        Returns:
            dict: A dictionary containing 'lat', 'lon', 'alt', and 'time'.
        """
        with self._lock:
            # Return a shallow copy
            return self.last_value

    def get_connected(self) -> bool:
        """
        Returns whether the GPS is connected.

        Returns:
            bool: True if GPS is connected, False otherwise.
        """
        with self._lock:
            return self.connected

    def stop(self):
        """
        Stops the thread cleanly.
        """
        self.running = False
