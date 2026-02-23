import customtkinter as ctk

from src.Domain.option import Option

class ConfirmationDialog:
    def __init__(self, parent, option: Option, price_text: str, distance: float, on_confirm=None):
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
        self._price_text = price_text
        self._distance = distance

        # Create custom confirmation dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Confirmation")
        self.dialog.geometry("550x270")
        self.dialog.resizable(False, False)
        self.dialog.attributes("-topmost", True)
        self.dialog.overrideredirect(True)
        self.dialog.configure(cursor="none")

        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (270 // 2)
        self.dialog.geometry(f"550x270+{x}+{y}")

        # Main frame with black border
        main_frame = ctk.CTkFrame(
            self.dialog,
            corner_radius=0,
            border_width=3,
            border_color="black"
        )
        main_frame.pack(fill="both", expand=True)

        services = ""
        for service in option.charging_station.services:
            services += service.type + " "

        duration = option.duration_seconds
        h, r = divmod(duration, 3600)
        m, _ = divmod(r, 60)

        text = f"{option.charging_station.name} selected!\n{services}\n\uf017 {h:.0f}h {m}m \uf153 {price_text} \uf4d7 {self._distance:.1f}km"

        # Message label
        label = ctk.CTkLabel(
            main_frame,
            text=text,
            font=ctk.CTkFont(family="Arial", size=40),
            wraplength=550
        )
        label.pack(pady=20)

        # Button frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        # Yes button
        btn_yes = ctk.CTkButton(
            button_frame,
            text="Yes",
            width=190,
            height=60,
            corner_radius=8,
            font=ctk.CTkFont(size=22),
            cursor="none",
            fg_color="green",
            hover_color="darkgreen",
            command=self._on_yes
        )
        btn_yes.pack(side="left", padx=10)

        # No button
        btn_no = ctk.CTkButton(
            button_frame,
            text="No",
            width=190,
            height=60,
            corner_radius=8,
            font=ctk.CTkFont(size=22),
            cursor="none",
            fg_color="red",
            hover_color="darkred",
            command=self._on_no
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
