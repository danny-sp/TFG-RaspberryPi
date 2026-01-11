import customtkinter as ctk
from tkintermapview import TkinterMapView
import time
import math
from .emergent import ConfirmationDialog

class TouchMapView(TkinterMapView):
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

class AppUI(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.position = self.controller.get_position()

        self.title("TFG - Simulador EV")
        self.geometry("800x480")
        self.attributes("-fullscreen", True)
        self.config(cursor="none")

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._setup_map()
        self._setup_controls()
        self._set_car_marker()

        self.controller.ui_callback = self.update_interface_safe

    def _set_car_marker(self):
        self.position = self.controller.get_position()
        print(f"Current position: {self.position}")
        self.map_widget.set_marker(self.position[0], self.position[1], text="You")
        self.map_widget.set_position(self.position[0], self.position[1])

    def _setup_map(self):
        self.map_widget = TouchMapView(self, corner_radius=0)
        self.map_widget.grid(row=0, column=0, sticky="nsew")
        self.map_widget.configure(cursor="none")

        self._set_car_marker()
        self.map_widget.set_zoom(10)

    def _setup_controls(self):
        self.frame_controls = ctk.CTkFrame(self, corner_radius=0)
        self.frame_controls.grid(row=0, column=1, sticky="nsew")
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
            corner_radius=10,
            font=ctk.CTkFont(size=20, weight="bold"),
            cursor="none"
        )
        self.btn_action.pack(side="top", pady=20)

        # Container for dynamic content
        self.content_container = ctk.CTkFrame(self.frame_controls, fg_color="transparent")
        self.content_container.pack(side="top", fill="both", expand=True, padx=10, pady=10)

    def _on_button_click(self):
        # Remove all markers except the car
        self._reset_state()

        charging_stations = self.controller.get_stations()
        self._set_car_marker()

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
            width=150,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            cursor="none",
            command=self._reset_state,
            fg_color="red",
            hover_color="red"
        )
        btn_cancel.pack(pady=10)

        for station in charging_stations:
            lat, lon = station.get_location()
            self.map_widget.set_marker(lat, lon, text=station.id)

            btn_station = ctk.CTkButton(
            self.scrollable_frame,
            text=station.id,
            width=150,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            cursor="none",
            command=lambda s=station: self._on_station_click(s)
            )
            btn_station.pack(pady=10)

    def _reset_state(self):
        self.map_widget.delete_all_marker()
        self.map_widget.set_marker(39.54505007110555, -4.328554881757664, text="You")

        # Remove old scroller
        if hasattr(self, 'scrollable_frame') and self.scrollable_frame is not None:
            try:
                self.scrollable_frame.pack_forget()
                self.scrollable_frame.destroy()
            except:
                pass
            self.scrollable_frame = None

    def _on_station_click(self, station):
        text = f"Are you sure you want to go to the charging station\n'{station.id}'?"
        ConfirmationDialog(
            self,
            text,
            on_confirm=lambda: self.controller.select_station(station)
        )

    def update_interface_safe(self, data):
        self.after(0, lambda: self._update_widgets(data))

    def _update_widgets(self, data):
        pass