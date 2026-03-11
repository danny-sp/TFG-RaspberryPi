import customtkinter as ctk
from tkintermapview import TkinterMapView
import time
import math
import os
import tkinter as tk

from src.Presentation.emergent import ConfirmationDialog

from src.Domain.controller import Controller

from src.Domain.control_position import ControlPosition
from src.Domain.control_requests import ControlRequests
from src.Domain.control_route import ControlRoute

from src.Domain.option import Option

from src.Utils.constants import Destinations

from src.Utils.logger import setup_logger

MAX_ZOOM_LEVEL = 17
MIN_ZOOM_LEVEL = 5

class TouchMapView(TkinterMapView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_mouse_down_position = None
        self.last_mouse_down_time = None
        self._moved = False

    def mouse_move(self, event):
        if self.last_mouse_down_position is None:
            self.last_mouse_down_position = (event.x, event.y)
            self.last_mouse_down_time = time.time()
            return

        dx = event.x - self.last_mouse_down_position[0]
        dy = event.y - self.last_mouse_down_position[1]
        distance = math.sqrt(dx*dx + dy*dy)

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
    def __init__(self, parent, controller: ControlPosition, destination: str, gps_thread):
        super().__init__(parent)
        self._logger = setup_logger("AppUIFrame")
        self._logger.info(f"Initializing AppUIFrame with destination: {destination}")
        self._parent = parent
        self._gps_controller = controller
        self._position = self._gps_controller.get_position()
        self._gps_thread = gps_thread
        self._destination = destination

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
            self._logger.warning("Car icon not found at assets/car.png - using default marker")

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self._setup_top_bar()
        self._setup_map()
        self._setup_route()
        self._setup_controls()

        self._car_marker = self._map_widget.set_marker(self._position[0], self._position[1], text=None, icon=self._car_icon, icon_anchor="center")
        self._map_widget.set_position(self._position[0], self._position[1])
        self._auto = True
        self._auto_timer = 5

        self._update()


##############################################################
##
## MAIN UI SETUP METHODS: TOP BAR, MAP, ROUTE, CONTROLS
##
##############################################################

    def _setup_top_bar(self):
        self._top_bar = ctk.CTkFrame(self, fg_color="#2a2a2a", height=50, corner_radius=0)
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
            cursor="none"
        )
        self._btn_close.pack(side="left")

        # GPS status label
        self._lbl_gps = ctk.CTkLabel(
            self._top_bar,
            text="GPS",
            font=ctk.CTkFont(family="Arial", size=25, weight="bold"),
            text_color="red"
        )
        self._lbl_gps.pack(side="top", pady=0)
        self._lbl_gps.place(relx=0.5, rely=0.5, anchor="center")

        # Clock label
        self._lbl_clock = ctk.CTkLabel(
            self._top_bar,
            text="",
            font=ctk.CTkFont(family="Arial", size=25, weight="bold"),
            text_color="white"
        )
        self._lbl_clock.pack(side="right", padx=20)

    def _setup_map(self):
        self._map_widget = TouchMapView(self, corner_radius=0, database_path="offline_map.db")
        self._map_widget.grid(row=1, column=0, sticky="nsew")
        self._map_widget.configure(cursor="none")

        self._map_widget.set_zoom(10)

        try:
            if hasattr(self._map_widget, "button_zoom_in"):
                self._map_widget.canvas.itemconfig(self._map_widget.button_zoom_in.canvas_rect, state='hidden')
                self._map_widget.canvas.itemconfig(self._map_widget.button_zoom_in.canvas_text, state='hidden')

            if hasattr(self._map_widget, "button_zoom_out"):
                self._map_widget.canvas.itemconfig(self._map_widget.button_zoom_out.canvas_rect, state='hidden')
                self._map_widget.canvas.itemconfig(self._map_widget.button_zoom_out.canvas_text, state='hidden')

            # Zoom In Button
            self._btn_zoom_in = ctk.CTkButton(
                self._map_widget,
                text="\uf067",
                width=80,
                height=80,
                corner_radius=0,
                font=ctk.CTkFont(family="Font Awesome 6 Free", size=40, weight="bold"),
                fg_color="gray",
                hover_color="gray",
                command=self._map_zoom_in,
                cursor="none"
            )
            self._btn_zoom_in.place(relx=0.03, rely=0.14, anchor="w")

            # Zoom Out Button
            self._btn_zoom_out = ctk.CTkButton(
                self._map_widget,
                text="\uf068",
                width=80,
                height=80,
                corner_radius=0,
                font=ctk.CTkFont(family="Font Awesome 6 Free", size=40, weight="bold"),
                fg_color="gray",
                hover_color="gray",
                command=self._map_zoom_out,
                cursor="none"
            )
            self._btn_zoom_out.place(relx=0.20, rely=0.14, anchor="w")

            self._btn_center = ctk.CTkButton(
                self._map_widget,
                text="\uf601",
                width=80,
                height=80,
                corner_radius=0,
                font=ctk.CTkFont(family="Font Awesome 6 Free", size=40, weight="bold"),
                fg_color="gray",
                hover_color="gray",
                command=self._map_center,
                cursor="none"
            )
            self._btn_center.place(relx=0.37, rely=0.14, anchor="w")

        except Exception as e:
            self._logger.warning(f"Using default zoom buttons due to error: {e}")

    def _setup_route(self):
        if isinstance(self._destination, str) and self._destination != "NONE":
            self._logger.info(f"Fetching route for destination: {self._destination}")
            response = ControlRoute.get_route_str(self._position, self._destination)
            if response is not None:
                route, distance, duration = response
                self._map_widget.set_path(route)

        elif isinstance(self._destination, tuple) and len(self._destination) == 2:
            self._logger.info(f"Fetching route for custom coordinates: {self._destination}")
            response = ControlRoute.get_route_coords(self._position, self._destination)
            if response is not None:
                route, distance, duration = response
                self._map_widget.set_path(route)

    def _setup_controls(self):
        self.frame_controls = ctk.CTkFrame(self, corner_radius=0)
        self.frame_controls.grid(row=1, column=1, sticky="nsew")
        self.frame_controls.configure(cursor="none")

        # Stop button - fixed at the top
        self.btn_action = ctk.CTkButton(
            self.frame_controls,
            text="Stop",
            fg_color="green",
            hover_color="green",
            command=self._on_button_click,
            width=200,
            height=50,
            corner_radius=0,
            font=ctk.CTkFont(family="Arial", size=30),
            cursor="none"
        )
        self.btn_action.pack(side="top", pady=20)

        # Container for dynamic content
        self.content_container = ctk.CTkFrame(self.frame_controls, fg_color="transparent")
        self.content_container.pack(side="top", fill="both", expand=True, padx=10, pady=10)

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
        self._logger.debug(f"Current position: {self._position}")
        self._car_marker.set_position(self._position[0], self._position[1])

    def _reset_state(self):
        self._map_widget.delete_all_marker()
        self._set_car_marker()

        # Remove old scroller
        if hasattr(self, 'scrollable_frame') and self.scrollable_frame is not None:
            try:
                self.scrollable_frame.pack_forget()
                self.scrollable_frame.destroy()
            except:
                pass
            self.scrollable_frame = None

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
            self._auto_timer = 5
            self._map_widget.moved = False

        if self._auto:
            self._map_center()
        else:
            if self._auto_timer > 0:
                self._auto_timer -= 1
            else:
                self._auto = True

        self.after(1000, self._update)


##############################################################
##
## BUTTONs CLICK HANDLERS
##
##############################################################

    def _on_button_click(self):
        # Remove all markers except the car
        self._reset_state()
        self._set_car_marker()
        # options = Controller.get_stations()
        dest_coords = Destinations[self._destination].value if self._destination in Destinations.__members__ else None

        options = ControlRequests.make_request(self._position, dest_coords)
        if not options:
            self._logger.warning("No options received for the request")
            return

        # Create a scrollable frame for station buttons
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.content_container,
            corner_radius=0,
            fg_color="transparent"
        )

        self.scrollable_frame.pack(fill="both", expand=True)
        btn_cancel = ctk.CTkButton(
            self.scrollable_frame,
            text="Cancel",
            width=200,
            height=40,
            corner_radius=0,
            font=ctk.CTkFont(family="Arial", size=30),
            cursor="none",
            command=self._reset_state,
            fg_color="red",
            hover_color="red"
        )
        btn_cancel.pack(pady=10)

        for o in options:
            lat, lon = o.charging_station.latitude, o.charging_station.longitude
            self._map_widget.set_marker(lat, lon, text=o.charging_station.name)
            distance = ControlRoute.get_distance_coords(self._position, (lat, lon))
            price_text = f"{o.price:.2f}"

            btn_station = ctk.CTkButton(
            self.scrollable_frame,
            text=f"{o.charging_station.name}\n{distance:.2f} km {price_text} €",
            width=200,
            height=80,
            corner_radius=0,
            font=ctk.CTkFont(family="Arial", size=30),
            cursor="none",
            command=lambda s=o, p=price_text, d=distance: self._on_option_click(s, p, d)
            )
            btn_station.pack(pady=10)


    def _on_option_click(self, option: Option, price_text: str, distance: float):
        ConfirmationDialog(
            self,
            option,
            price_text,
            distance,
            on_confirm=lambda: self._controller.select_station(option)
        )
