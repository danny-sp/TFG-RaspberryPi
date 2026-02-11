import customtkinter as ctk
import tkinter as tk
from typing import Callable, Optional


class WelcomeFrame(ctk.CTkFrame):
    def __init__(self, parent, on_select: Optional[Callable[[str], None]] = None):
        super().__init__(parent)
        self.parent = parent
        self.on_select = on_select
        self.selected: Optional[str] = None

        # Ensure the root window is fullscreen and hidden cursor
        try:
            self.parent.title("TFG - Welcome")
            self.parent.geometry("800x480")
            self.parent.attributes("-fullscreen", True)
            self.parent.config(cursor="none")
        except Exception:
            pass

        # Layout: 2x2 grid for four big buttons
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        btn_style = dict(width=400, height=200, corner_radius=0, font=ctk.CTkFont(family="Arial", size=40))

        self.btn_bilbao = ctk.CTkButton(self, text="BILBAO", fg_color="#0078D7", hover_color="#005A9E",
                                        command=lambda: self._select("BILBAO"), **btn_style, cursor="none")
        self.btn_bilbao.grid(row=0, column=0, sticky="nsew")

        self.btn_madrid = ctk.CTkButton(self, text="MADRID", fg_color="#0078D7", hover_color="#005A9E",
                                        command=lambda: self._select("MADRID"), **btn_style, cursor="none")
        self.btn_madrid.grid(row=0, column=1, sticky="nsew")

        self.btn_none = ctk.CTkButton(self, text="NONE", fg_color="#0078D7", hover_color="#005A9E",
                                       command=lambda: self._select("NONE"), **btn_style, cursor="none")
        self.btn_none.grid(row=1, column=0, sticky="nsew")

        self.btn_exit = ctk.CTkButton(self, text="EXIT", fg_color="#D32F2F", hover_color="#B71C1C",
                                      command=lambda: self._select("EXIT"), **btn_style, cursor="none")
        self.btn_exit.grid(row=1, column=1, sticky="nsew")

    def _select(self, city: str):
        self.selected = city
        if self.on_select:
            try:
                self.on_select(city)
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
