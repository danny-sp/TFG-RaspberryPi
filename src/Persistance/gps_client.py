import gpsd
import threading
import time

class GpsPoll(threading.Thread):
    def __init__(self):
        super().__init__()
        gpsd.connect()
        self.last_value = None
        self.running = True
        self.connected = False
        self._lock = threading.Lock() # Avoids race conditions

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
                            'lat': packet.lat,
                            'lon': packet.lon,
                            'alt': packet.alt if packet.mode >= 3 else None,
                            'time': packet.time
                        }
                else:
                    with self._lock:
                        self.connected = False
                time.sleep(1)  # Poll every second
        except Exception as e:
            print(f"Error en el hilo GPS: {e}")
            self.connected = False

    def get_data(self):
        """
        Returns the last known GPS position
        """
        with self._lock:
            print("Getting GPS data...", self.last_value)
            # Return a shallow copy
            return self.last_value

    def get_connected(self):
        """
        Returns whether the GPS is connected
        """
        with self._lock:
            return self.connected

    def stop(self):
        """Stops the thread cleanly"""
        self.running = False