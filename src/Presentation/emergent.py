"""
Custom confirmation dialog for user interactions.
"""

import os
from typing import Tuple

import customtkinter as ctk  # type: ignore
from PIL import Image

from src.Domain.control_route import ControlRoute
from src.Domain.option import Option


class ConfirmationDialog:
    """
    Custom confirmation dialog that displays information about a selected charging station option and asks the user to confirm their choice.
    """

    def __init__(
        self, parent, option: Option, position: Tuple[float, float], on_confirm=None
    ):
        """
        Create a custom confirmation dialog.

        Args:
            parent: The parent window
            option: The Option object containing the charging station information
            price_text: The price text to display
            distance: The distance to the charging station
            on_confirm: Callback function to call when user clicks "YES"
        """
        self.on_confirm = on_confirm
        self._price_text = f"{option.price:.2f}"
        self._distance = ControlRoute.get_distance_coords(
            position, option.charging_station.location
        )

        operators = [
            "Electromaps",
            "Endesa",
            "Etecnic",
            "Iberdrola",
            "Mercadona",
            "Repsol",
        ]
        operator_name = option.charging_station.operator
        if operator_name in operators:
            logo_path = f"./assets/operators/{operator_name}.png"
        else:
            logo_path = None

        # Create custom confirmation dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Confirmation")
        self.dialog.geometry("570x270")
        self.dialog.resizable(False, False)
        self.dialog.attributes("-topmost", True)
        self.dialog.overrideredirect(True)
        self.dialog.configure(cursor="none")

        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (570 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (270 // 2)
        self.dialog.geometry(f"570x270+{x}+{y}")

        # Main frame with black border
        main_frame = ctk.CTkFrame(
            self.dialog, corner_radius=0, border_width=3, border_color="black"
        )
        main_frame.pack(fill="both", expand=True)

        services = set()

        for service in option.services_nearby:
            services.add(service)

        services_str = " ".join(services)
        duration = option.charging_hours * 3600
        h, r = divmod(duration, 3600)
        m, _ = divmod(r, 60)

        text = f"{option.charging_station.name} selected!"
        logo_image = None
        if logo_path and os.path.exists(logo_path):
            image = Image.open(logo_path)
            logo_image = ctk.CTkImage(
                light_image=image, dark_image=image, size=(70, 70)
            )
        self._logo_image = logo_image

        # Message label
        label = ctk.CTkLabel(
            main_frame,
            text=text,
            font=ctk.CTkFont(family="Arial", size=40),
            wraplength=540,
            image=self._logo_image,
            compound="left",
        )
        label.pack(pady=5)

        info_text = f"\uf017 {h:.0f}h {m}m \uf153 {self._price_text} \uf4d7 {self._distance:.1f}km"
        info_lbl = ctk.CTkLabel(
            main_frame,
            text=info_text,
            font=ctk.CTkFont(family="Font Awesome 6 Free Solid", size=30),
        )
        info_lbl.pack(pady=5)

        services_lbl = ctk.CTkLabel(
            main_frame,
            text=f"{services_str}",
            font=ctk.CTkFont(family="Font Awesome 6 Free Solid", size=30),
        )
        services_lbl.pack(pady=10)

        # Button frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        # Yes button
        btn_yes = ctk.CTkButton(
            button_frame,
            text="Yes",
            width=190,
            height=80,
            corner_radius=8,
            font=ctk.CTkFont(size=22),
            cursor="none",
            fg_color="green",
            hover_color="darkgreen",
            command=self._on_yes,
        )
        btn_yes.pack(side="left", padx=10)

        # No button
        btn_no = ctk.CTkButton(
            button_frame,
            text="No",
            width=190,
            height=80,
            corner_radius=8,
            font=ctk.CTkFont(size=22),
            cursor="none",
            fg_color="red",
            hover_color="darkred",
            command=self._on_no,
        )
        btn_no.pack(side="left", padx=10)

        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()

    def _on_yes(self):
        """Handle Yes button click"""
        self.dialog.destroy()
        if self.on_confirm:
            self.on_confirm()

    def _on_no(self):
        """Handle No button click"""
        self.dialog.destroy()


class StopConfirmationDialog:
    """
    Custom confirmation dialog to ask the user if they want to stop going to the charging station.
    """

    def __init__(self, parent, on_confirm=None):
        self.on_confirm = on_confirm

        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Confirmation")
        self.dialog.geometry("530x230")
        self.dialog.resizable(False, False)
        self.dialog.attributes("-topmost", True)
        self.dialog.overrideredirect(True)
        self.dialog.configure(cursor="none")

        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (530 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (230 // 2)
        self.dialog.geometry(f"530x230+{x}+{y}")

        main_frame = ctk.CTkFrame(
            self.dialog, corner_radius=0, border_width=3, border_color="black"
        )
        main_frame.pack(fill="both", expand=True)

        label = ctk.CTkLabel(
            main_frame,
            text="Are you sure you want to stop going to charging station?",
            font=ctk.CTkFont(family="Arial", size=35),
            wraplength=540,
        )
        label.pack(pady=40)

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        btn_yes = ctk.CTkButton(
            button_frame,
            text="Yes",
            width=190,
            height=80,
            corner_radius=8,
            font=ctk.CTkFont(size=22),
            cursor="none",
            fg_color="green",
            hover_color="darkgreen",
            command=self._on_yes,
        )
        btn_yes.pack(side="left", padx=10)

        btn_no = ctk.CTkButton(
            button_frame,
            text="No",
            width=190,
            height=80,
            corner_radius=8,
            font=ctk.CTkFont(size=22),
            cursor="none",
            fg_color="red",
            hover_color="darkred",
            command=self._on_no,
        )
        btn_no.pack(side="left", padx=10)

        self.dialog.transient(parent)
        self.dialog.grab_set()

    def _on_yes(self):
        self.dialog.destroy()
        if self.on_confirm:
            self.on_confirm()

    def _on_no(self):
        self.dialog.destroy()
