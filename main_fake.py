"""
Offline / fake entry point for the EV charging application.

Replaces every external dependency with local fakes so the app can run
without internet, GPS hardware, or an MQTT broker:

  · FakeGpsPoll     → replays route.nmea instead of real GPS
  · FakeRouteClient → builds routes from the NMEA track offline
  · FakeMqttService → returns hard-coded charging options

Usage:
    python main_fake.py
"""

import sys
import types
import tkinter as tk

import customtkinter as ctk
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Import the fake implementations first (they have no external dependencies)
# ---------------------------------------------------------------------------
from src.Persistence.fake_gps_client import FakeGpsPoll
from src.Persistence.fake_route_client import FakeRouteClient
from src.Persistence.fake_mqtt_client import FakeMqttService

# ---------------------------------------------------------------------------
# Inject fake modules into sys.modules BEFORE any real module is imported.
#
# This prevents Python from ever executing the real module code (which runs
# gpsd.connect() and mqtt.Client().connect() at class-definition time).
# ---------------------------------------------------------------------------

def _fake_module(name: str, **attrs) -> types.ModuleType:
    """Creates and registers a fake module with the given attributes."""
    mod = types.ModuleType(name)
    mod.__dict__.update(attrs)
    sys.modules[name] = mod
    return mod

# Fake src.Persistence.gps_client  — exposes GpsPoll = FakeGpsPoll
_fake_module("src.Persistence.gps_client", GpsPoll=FakeGpsPoll)

# Fake src.Persistence.route_client — exposes RouteClient = FakeRouteClient
_fake_module("src.Persistence.route_client", RouteClient=FakeRouteClient)

# Fake src.Persistence.mqtt_client  — exposes MqttService = FakeMqttService
_fake_module("src.Persistence.mqtt_client", MqttService=FakeMqttService)

# ---------------------------------------------------------------------------
# Now import the real application modules (patches are already active)
# ---------------------------------------------------------------------------
from src.Domain.control_position import ControlPosition
from src.Presentation.presentation import AppUIFrame
from src.Presentation.welcome import WelcomeFrame
from src.Utils.logger import setup_logger


def on_welcome_select(destination: str):
    """
    Handles the selection of a destination from the welcome screen
    and initialises the main application frame.
    """
    global logger, welcome_frame, root, gps_controller, gps_thread

    if destination == "EXIT":
        logger.info("EXIT selected — stopping.")
        root.quit()
        return
    elif destination == "NONE":
        logger.info("No destination selected. Navigating without route.")
    else:
        logger.info(f"Destination selected: {destination}")

    try:
        welcome_frame.pack_forget()
        welcome_frame.destroy()
    except Exception:
        pass

    logger.info("Initialising main application frame (FAKE mode)…")
    app_frame = AppUIFrame(root, gps_controller, destination, gps_thread)
    app_frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    logger = setup_logger("main_fake")
    logger.info("=" * 60)
    logger.info("Starting in OFFLINE / FAKE mode")
    logger.info("  GPS   → FakeGpsPoll   (route.nmea)")
    logger.info("  Route → FakeRouteClient (offline, from route.nmea)")
    logger.info("  MQTT  → FakeMqttService (hard-coded options)")
    logger.info("=" * 60)

    root = ctk.CTk()

    # Start the fake GPS thread
    gps_thread = FakeGpsPoll()
    gps_thread.start()
    gps_controller = ControlPosition(gps_client=gps_thread)

    selected_dest = tk.StringVar(root, value="")

    def _on_selected_var(*args):
        dest = selected_dest.get()
        if dest:
            on_welcome_select(dest)

    selected_dest.trace_add("write", _on_selected_var)

    welcome_frame = WelcomeFrame(root, selected_var=selected_dest)
    welcome_frame.pack(fill="both", expand=True)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Closing application…")
        try:
            gps_thread.stop()
        except Exception:
            pass
        try:
            root.quit()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

