"""
Welcome screen frame that allows the user to select a destination or exit the application.
"""

import tkinter as tk
from typing import Callable, Optional

import customtkinter as ctk  # type: ignore


class WelcomeFrame(ctk.CTkFrame):
    """
    Welcome screen frame that allows the user to select a destination or exit the application.
    """

    def __init__(
        self,
        parent,
        on_select: Optional[Callable[[str], None]] = None,
        selected_var: Optional[tk.StringVar] = None,
    ):
        super().__init__(parent)
        self._parent = parent
        self._on_select = on_select
        self._selected_var = selected_var
        self._selected: Optional[str] = None

        # Ensure the root window is fullscreen and hidden cursor
        try:
            self._parent.title("TFG - Welcome")
            self._parent.geometry("800x480")
            self._parent.attributes("-fullscreen", True)
            self._parent.config(cursor="none")
        except Exception:
            pass

        # Layout: 2x2 grid for four big buttons
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # small rounded border around each button
        btn_style = {
            "width": 400,
            "height": 200,
            "corner_radius": 20,
            "border_width": 3,
            "font": ctk.CTkFont(family="Arial", size=40),
        }

        self.btn_bilbao = ctk.CTkButton(
            self,
            text="BILBAO",
            fg_color="#0078D7",
            hover_color="#0078D7",
            border_color="#ffffff",
            command=lambda: self._select("BILBAO"),
            **btn_style,
            cursor="none",
        )
        self.btn_bilbao.grid(row=0, column=0, sticky="nsew")

        self.btn_madrid = ctk.CTkButton(
            self,
            text="MADRID",
            fg_color="#0078D7",
            hover_color="#0078D7",
            border_color="#ffffff",
            command=lambda: self._select("MADRID"),
            **btn_style,
            cursor="none",
        )
        self.btn_madrid.grid(row=0, column=1, sticky="nsew")

        self.btn_none = ctk.CTkButton(
            self,
            text="NONE",
            fg_color="#0078D7",
            hover_color="#0078D7",
            border_color="#ffffff",
            command=lambda: self._select("NONE"),
            **btn_style,
            cursor="none",
        )
        self.btn_none.grid(row=1, column=0, sticky="nsew")

        self.btn_exit = ctk.CTkButton(
            self,
            text="EXIT",
            fg_color="#D32F2F",
            hover_color="#D32F2F",
            border_color="#ffffff",
            command=lambda: self._select("EXIT"),
            **btn_style,
            cursor="none",
        )
        self.btn_exit.grid(row=1, column=1, sticky="nsew")

    def _select(self, city: str):
        self._selected = city

        selected_var = self._selected_var
        if selected_var is not None:
            try:
                selected_var.set(city)
            except Exception:
                pass
        elif self._on_select:
            try:
                self._on_select(city)
            except Exception:
                pass

        try:
            for w in (self.btn_bilbao, self.btn_madrid, self.btn_none, self.btn_exit):
                try:
                    w.configure(state="disabled")
                except Exception:
                    pass
        except Exception:
            pass
