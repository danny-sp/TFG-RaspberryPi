import gpsd
import threading
import time

class GpsPoll(threading.Thread):
    def __init__(self):
        super().__init__()
        gpsd.connect()
        self.current_value = None
        self.running = True
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
                        self.current_value = {
                            'lat': packet.lat,
                            'lon': packet.lon,
                            'alt': packet.alt if packet.mode >= 3 else None,
                            'time': packet.time
                        }
                time.sleep(1)  # Poll every second
        except Exception as e:
            print(f"Error en el hilo GPS: {e}")

    def get_data(self):
        """
        Returns the last known GPS position
        """
        with self._lock:
            # Return a shallow copy
            return self.current_value

    def stop(self):
        """Stops the thread cleanly"""
        self.running = False