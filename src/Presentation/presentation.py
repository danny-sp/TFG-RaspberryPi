"""
Main application frame that contains the map, controls, and handles user interactions.
"""

import math
import os
import threading
import time
import tkinter as tk
from datetime import datetime, timedelta

import customtkinter as ctk  # type: ignore
from tkintermapview import TkinterMapView  # type: ignore

from src.Domain.control_position import ControlPosition
from src.Domain.control_requests import ControlRequests
from src.Domain.control_route import ControlRoute
from src.Domain.option import Option
from src.Presentation.emergent import (ConfirmationDialog,
                                       StopConfirmationDialog)
from src.Utils.constants import Destinations
from src.Utils.logger import setup_logger

MAX_ZOOM_LEVEL = 17
MIN_ZOOM_LEVEL = 5


class TouchMapView(TkinterMapView):
    """
    Custom MapView for tactile screens interaction.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_mouse_down_position = None
        self.last_mouse_down_time = None
        self._moved = False

    def mouse_move(self, event):
        """
        Override mouse move to detect if the user is dragging the map or just tapping.
        """
        if self.last_mouse_down_position is None:
            self.last_mouse_down_position = (event.x, event.y)
            self.last_mouse_down_time = time.time()
            return

        dx = event.x - self.last_mouse_down_position[0]
        dy = event.y - self.last_mouse_down_position[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 50:
            self.last_mouse_down_position = (event.x, event.y)
            self.last_mouse_down_time = time.time()
        else:
            super().mouse_move(event)
            self._moved = True

    @property
    def moved(self):
        return self._moved

    @moved.setter
    def moved(self, value):
        self._moved = value


class AppUIFrame(ctk.CTkFrame):
    """
    Main application frame that contains the map, controls, and handles user interactions.
    """

    def __init__(
        self, parent, controller: ControlPosition, destination: str, gps_thread
    ):
        super().__init__(parent)
        self._logger = setup_logger("AppUIFrame")
        self._logger.info(f"Initializing AppUIFrame with destination: {destination}")
        self._parent = parent
        self._gps_controller = controller
        self._position = self._gps_controller.get_position()
        self._gps_thread = gps_thread
        self._destination = destination
        self._going_to_station = False

        self._car_icon = None
        TARGET_CAR_ICON_SIZE = 50

        if os.path.exists("assets/car.png"):
            try:
                img = tk.PhotoImage(file="assets/car.png")
                w, h = img.width(), img.height()
                scale = max(1, int(max(w, h) / TARGET_CAR_ICON_SIZE))
                if scale > 1:
                    img = img.subsample(scale, scale)
                self._car_icon = img
            except Exception as e:
                self._logger.error(f"Failed to load car icon: {e}")
        else:
            self._logger.warning(
                "Car icon not found at assets/car.png - using default marker"
            )

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self._setup_top_bar()
        self._setup_map()
        self._setup_controls()
        self._setup_route()

        self._map_widget.set_position(self._position[0], self._position[1])
        self._map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google normal

        self._auto = True
        self._auto_timer = 5

        self._update()

    ##############################################################
    ##
    ## HELPERS
    ##
    ##############################################################

    def _destroy_widget(self, widget_name):
        """Safely destroys a widget by its attribute name if it exists."""
        widget = getattr(self, widget_name, None)
        if widget is not None:
            widget.pack_forget()
            widget.destroy()
            setattr(self, widget_name, None)

    @property
    def target_name(self) -> str:
        return self._destination if isinstance(self._destination, str) else "Custom"

    def _get_route_to_destination(self, start_coords):
        """Fetches the route depending on whether destination is a string or coordinates."""
        if isinstance(self._destination, str) and self._destination != "NONE":
            return ControlRoute.get_route_str(start_coords, self._destination)
        elif isinstance(self._destination, tuple) and len(self._destination) == 2:
            return ControlRoute.get_route_coords(start_coords, self._destination)
        return None

    ##############################################################
    ##
    ## MAIN UI SETUP METHODS: TOP BAR, MAP, ROUTE, CONTROLS
    ##
    ##############################################################

    def _setup_top_bar(self):
        self._top_bar = ctk.CTkFrame(
            self, fg_color="#2a2a2a", height=50, corner_radius=0
        )
        self._top_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self._top_bar.grid_propagate(False)
        self._top_bar.configure(cursor="none")

        # Close program button
        self._btn_close = ctk.CTkButton(
            self._top_bar,
            text="\uf00d",
            width=50,
            height=50,
            corner_radius=0,
            font=ctk.CTkFont(family="Font Awesome 6 Free", size=24, weight="bold"),
            fg_color="red",
            hover_color="red",
            command=self.close_app,
            cursor="none",
        )
        self._btn_close.pack(side="left")

        # GPS status label
        self._lbl_gps = ctk.CTkLabel(
            self._top_bar,
            text="GPS",
            font=ctk.CTkFont(family="Arial", size=25, weight="bold"),
            text_color="red",
        )
        self._lbl_gps.pack(side="top", pady=0)
        self._lbl_gps.place(relx=0.5, rely=0.5, anchor="center")

        # Clock label
        self._lbl_clock = ctk.CTkLabel(
            self._top_bar,
            text="",
            font=ctk.CTkFont(family="Arial", size=25, weight="bold"),
            text_color="white",
        )
        self._lbl_clock.pack(side="right", padx=20)

    def _create_map_button(self, text, x_pos, command):
        btn = ctk.CTkButton(
            self._map_widget,
            text=text,
            width=80,
            height=80,
            corner_radius=0,
            font=ctk.CTkFont(family="Font Awesome 6 Free", size=40, weight="bold"),
            fg_color="gray",
            hover_color="gray",
            command=command,
            cursor="none",
        )
        btn.place(x=x_pos, rely=0.14, anchor="w")
        return btn

    def _setup_map(self):
        self._map_widget = TouchMapView(
            self, corner_radius=0, database_path="offline_map.db"
        )
        self._map_widget.grid(row=1, column=0, sticky="nsew")
        self._map_widget.configure(cursor="none")

        self._map_widget.set_zoom(10)

        try:
            if hasattr(self._map_widget, "button_zoom_in"):
                self._map_widget.canvas.itemconfig(
                    self._map_widget.button_zoom_in.canvas_rect, state="hidden"
                )
                self._map_widget.canvas.itemconfig(
                    self._map_widget.button_zoom_in.canvas_text, state="hidden"
                )

            if hasattr(self._map_widget, "button_zoom_out"):
                self._map_widget.canvas.itemconfig(
                    self._map_widget.button_zoom_out.canvas_rect, state="hidden"
                )
                self._map_widget.canvas.itemconfig(
                    self._map_widget.button_zoom_out.canvas_text, state="hidden"
                )

            # Map Controls
            self._btn_zoom_in = self._create_map_button("\uf067", 20, self._map_zoom_in)
            self._btn_zoom_out = self._create_map_button(
                "\uf068", 110, self._map_zoom_out
            )
            self._btn_center = self._create_map_button("\uf601", 200, self._map_center)
            self._btn_reroute = self._create_map_button(
                "\uf021", 290, self._setup_route
            )

        except Exception as e:
            self._logger.warning(f"Using default zoom buttons due to error: {e}")

    def _setup_route(self):
        # Remove existing route if any
        if self._going_to_station:
            StopConfirmationDialog(self, on_confirm=self._stop_station_navigation)
            return

        self._map_widget.delete_all_path()
        self._reset_state()

        if self._destination != "NONE":
            self._logger.info(f"Fetching route to destination: {self._destination}")
            response = self._get_route_to_destination(self._position)

            if response is not None:
                route, _, duration = response
                self._map_widget.set_path(route)

                eta = datetime.now() + timedelta(seconds=duration)
                self._show_destination_info(self.target_name, eta.strftime("%H:%M"))

    def _setup_controls(self):
        self._frame_controls = ctk.CTkFrame(self, corner_radius=0)
        self._frame_controls.grid(row=1, column=1, sticky="nsew")
        self._frame_controls.configure(cursor="none")
        self._frame_controls.grid_propagate(False)
        self._frame_controls.pack_propagate(False)

        # Stop button - fixed at the top
        self._btn_action = ctk.CTkButton(
            self._frame_controls,
            text="Stop",
            fg_color="green",
            hover_color="green",
            command=self._on_button_click,
            width=200,
            height=50,
            corner_radius=0,
            font=ctk.CTkFont(family="Arial", size=30),
            cursor="none",
        )
        self._btn_action.pack(side="top", pady=20)

        # Container for dynamic content
        self._content_container = ctk.CTkFrame(
            self._frame_controls, fg_color="transparent"
        )
        self._content_container.pack(
            side="top", fill="both", expand=True, padx=10, pady=10
        )

    ##############################################################
    ##
    ## AUXILIAR METHODS: CLOSE_APP, SET CAR MARKER, RESET_STATE, ZOOM, UPDATE GPS/CLK
    ##
    ##############################################################

    def close_app(self):
        """Safely closes the application"""
        self._gps_thread.stop()
        self.quit()

    def _set_car_marker(self):
        self._position = self._gps_controller.get_position()
        # self._logger.debug(f"Current position: {self._position}")
        self._car_marker.set_position(self._position[0], self._position[1])

    def _reset_state(self):
        self._map_widget.delete_all_marker()
        self._car_marker = self._map_widget.set_marker(
            self._position[0],
            self._position[1],
            text=None,
            icon=self._car_icon,
            icon_anchor="center",
        )

        self._destroy_widget("_scrollable_frame")
        self._destroy_widget("_station_info_frame")
        self._destroy_widget("_destination_info_frame")

    def _map_zoom_in(self):
        if self._map_widget.zoom < MAX_ZOOM_LEVEL:
            self._map_widget.set_zoom(self._map_widget.zoom + 1)
            self._auto = False
            self._auto_timer = 5

    def _map_zoom_out(self):
        if self._map_widget.zoom > MIN_ZOOM_LEVEL:
            self._map_widget.set_zoom(self._map_widget.zoom - 1)
            self._auto = False
            self._auto_timer = 5

    def _map_center(self):
        self._auto = True
        self._map_widget.set_position(self._position[0], self._position[1])
        self._map_widget.set_zoom(17)

    def _update(self):
        current_time = time.strftime("%H:%M:%S")
        self._lbl_clock.configure(text=current_time)

        if self._gps_controller.get_connected_gps():
            self._lbl_gps.configure(text="GPS: Connected", text_color="green")
        else:
            self._lbl_gps.configure(text="GPS: Disconnected", text_color="red")

        self._set_car_marker()

        if self._map_widget.moved:
            self._auto = False
            self._auto_timer = 10
            self._map_widget.moved = False

        if self._auto:
            self._map_center()
        else:
            if self._auto_timer > 0:
                self._auto_timer -= 1
            else:
                self._auto = True

        self.after(500, self._update)

    ##############################################################
    ##
    ## BUTTONs CLICK HANDLERS
    ##
    ##############################################################

    def _on_button_click(self):
        if self._going_to_station:
            StopConfirmationDialog(self, on_confirm=self._stop_station_navigation)
            return

        # Remove all markers except the car
        self._reset_state()

        dest_coords = (
            Destinations[self._destination].value
            if self._destination in Destinations.__members__
            else None
        )

        self._btn_action.configure(state="disabled", text="Waiting...")

        # Start a thread so the UI is not blocked while waiting for MQTT response
        threading.Thread(
            target=self._fetch_options_thread,
            args=(self._position, dest_coords),
            daemon=True,
        ).start()

    def _stop_station_navigation(self):
        self._going_to_station = False
        self._reset_state()
        self._setup_route()

    def _fetch_options_thread(self, position, dest_coords):
        options = ControlRequests.make_request(position, dest_coords)
        # Process options on the main thread
        self.after(0, self._process_options, options)

    def _process_options(self, options):
        self._btn_action.configure(state="normal", text="Stop")

        if not options:
            self._logger.warning("No options received for the request")
            return

        # Create a scrollable frame for station buttons
        self._scrollable_frame = ctk.CTkScrollableFrame(
            self._content_container, corner_radius=0, fg_color="transparent"
        )
        self._scrollable_frame._scrollbar.configure(width=40)
        self._scrollable_frame.pack(fill="both", expand=True)
        btn_cancel = ctk.CTkButton(
            self._scrollable_frame,
            text="Cancel",
            width=200,
            height=40,
            corner_radius=0,
            font=ctk.CTkFont(family="Arial", size=30),
            cursor="none",
            command=self._reset_state,
            fg_color="red",
            hover_color="red",
        )
        btn_cancel.pack(pady=10)

        for idx, o in enumerate(options):
            lat, lon = o.charging_station.latitude, o.charging_station.longitude

            if idx == 0:
                self._map_widget.set_marker(
                    lat,
                    lon,
                    text=o.charging_station.name,
                    marker_color_outside="#FFD700",
                )
            else:
                self._map_widget.set_marker(lat, lon, text=o.charging_station.name)

            distance = ControlRoute.get_distance_coords(self._position, (lat, lon))

            display_name = o.charging_station.name
            if len(display_name) > 13:
                display_name = display_name[:13] + "..."

            btn_station = ctk.CTkButton(
                self._scrollable_frame,
                text=f"{display_name}\n{distance:.2f} km {o.price:.2f} €",
                width=200,
                height=80,
                corner_radius=0,
                font=ctk.CTkFont(family="Arial", size=30),
                cursor="none",
                command=lambda s=o: self._on_option_click(s),
                anchor="w",
            )

            if idx == 0:
                btn_station.configure(
                    fg_color="#FFD700", hover_color="#CCAC00", text_color="black"
                )

            btn_station.pack(pady=10, fill="x", padx=10)

    def _on_option_click(self, option: Option):
        ConfirmationDialog(
            self,
            option,
            self._gps_controller.get_position(),
            on_confirm=lambda: self._option_selected(option),
        )

    def _option_selected(self, option: Option):
        self._reset_state()
        self._map_widget.delete_all_path()
        self._btn_action.configure(state="normal", text="Stop")
        self._going_to_station = True

        self._show_station_info(option)

        station_coords = (
            option.charging_station.latitude,
            option.charging_station.longitude,
        )

        # Route 1: Current position to Station (Red)
        self._logger.info(f"Fetching route to station: {station_coords}")
        resp1 = ControlRoute.get_route_coords(self._position, station_coords)
        if resp1 is not None:
            route1, _, _ = resp1
            self._map_widget.set_path(route1, color="red")

        # Route 2: Station to Destination (Green)
        self._logger.info(
            f"Fetching route from station to destination: {self._destination}"
        )
        duration2 = 0
        if self._destination != "NONE":
            resp2 = self._get_route_to_destination(station_coords)
            if resp2 is not None:
                route2, _, duration2 = resp2
                self._map_widget.set_path(route2, color="green")

        # Calculate ETA to destination (after charging)
        eta_dest = option.start_time + timedelta(
            hours=option.charging_hours, seconds=duration2
        )
        if self._destination != "NONE":
            self._show_destination_info(self.target_name, eta_dest.strftime("%H:%M"))

        self._map_widget.set_marker(
            station_coords[0],
            station_coords[1],
            text=option.charging_station.name,
            marker_color_outside="#FFD700",
        )

    def _create_icon_text(self, parent, icon, text):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        lbl_icon = ctk.CTkLabel(
            frame,
            text=icon,
            font=ctk.CTkFont(family="Font Awesome 6 Free", size=20, weight="bold"),
        )
        lbl_icon.pack(side="left", padx=(0, 5))
        lbl_text = ctk.CTkLabel(
            frame, text=text, font=ctk.CTkFont(family="Arial", size=20)
        )
        lbl_text.pack(side="left")
        return frame

    def _show_station_info(self, option: Option):
        self._station_info_frame = ctk.CTkFrame(
            self._content_container, corner_radius=10
        )
        self._station_info_frame.pack(fill="x", padx=10, pady=10)

        display_name = option.charging_station.name
        if len(display_name) > 16:
            display_name = display_name[:15] + "..."

        name_lbl = ctk.CTkLabel(
            self._station_info_frame,
            text=display_name,
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
        )
        name_lbl.pack(pady=(10, 5))

        details_frame = ctk.CTkFrame(self._station_info_frame, fg_color="transparent")
        details_frame.pack(fill="x", padx=10, pady=(0, 10))

        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_columnconfigure(1, weight=1)

        eta_time = option.start_time.strftime("%H:%M")
        charge_min = int(option.charging_hours * 60)

        # ETA (fa-road)
        f_eta = self._create_icon_text(details_frame, "\uf018", eta_time)
        f_eta.grid(row=0, column=0, pady=5, sticky="w", padx=10)

        # Charging time (fa-battery-full)
        f_charge = self._create_icon_text(details_frame, "\uf240", f"{charge_min} min")
        f_charge.grid(row=0, column=1, pady=5, sticky="w", padx=10)

        # Price (fa-euro-sign)
        f_price = self._create_icon_text(
            details_frame, "\uf153", f"{option.price:.2f} €"
        )
        f_price.grid(row=1, column=0, pady=5, sticky="w", padx=10)

        # Power (fa-bolt)
        f_power = self._create_icon_text(
            details_frame, "\uf0e7", f"{option.kw_speed} kW"
        )
        f_power.grid(row=1, column=1, pady=5, sticky="w", padx=10)

    def _show_destination_info(self, name, eta_str):
        self._destroy_widget("_destination_info_frame")

        self._destination_info_frame = ctk.CTkFrame(
            self._content_container, corner_radius=10
        )
        self._destination_info_frame.pack(fill="x", padx=10, pady=10)

        display_name = f"Dest: {name}"
        if len(display_name) > 16:
            display_name = display_name[:15] + "..."

        name_lbl = ctk.CTkLabel(
            self._destination_info_frame,
            text=display_name,
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
        )
        name_lbl.pack(pady=(10, 5))

        details_frame = ctk.CTkFrame(
            self._destination_info_frame, fg_color="transparent"
        )
        details_frame.pack(fill="x", padx=10, pady=(0, 10))

        # ETA to destination (fa-flag-checkered)
        f_eta = self._create_icon_text(details_frame, "\uf11e", eta_str)
        f_eta.pack(pady=5, anchor="center")
