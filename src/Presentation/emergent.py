import customtkinter as ctk

from src.Domain.option import Option

class ConfirmationDialog:
    def __init__(self, parent, option: Option, on_confirm=None):
        """
        Create a custom confirmation dialog.

        Args:
            parent: The parent window
            on_confirm: Callback function to call when user clicks "YES"
        """
        self.on_confirm = on_confirm

        # Create custom confirmation dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Confirmation")
        self.dialog.geometry("450x200")
        self.dialog.resizable(False, False)
        self.dialog.attributes("-topmost", True)
        self.dialog.overrideredirect(True)
        self.dialog.configure(cursor="none")

        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (200 // 2)
        self.dialog.geometry(f"450x200+{x}+{y}")

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

        text = f"{option.charging_station.name} selected!\n{services}"
        print(text)
        # Message label
        label = ctk.CTkLabel(
            main_frame,
            text=text,
            font=ctk.CTkFont(family="Arial", size=40),
            wraplength=450
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
            font=ctk.CTkFont(size=18),
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
            font=ctk.CTkFont(size=18),
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
