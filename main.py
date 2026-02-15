import customtkinter as ctk
import tkinter as tk

from src.Presentation.presentation import AppUIFrame
from src.Presentation.welcome import WelcomeFrame

from src.Domain.controller import Controller

from src.Persistance.gps_client import GpsPoll

from src.Utils.logger import setup_logger

def on_welcome_select(destination: str):
    global logger, welcome_frame, root, controller, gps_thread
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

    logger.info("Initializing main application frame...")
    app_frame = AppUIFrame(root, controller, destination, gps_thread)
    app_frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    logger = setup_logger("main")

    root = ctk.CTk()

    # start gps and controller
    gps_thread = GpsPoll()
    gps_thread.start()
    controller = Controller(gps_client=gps_thread)

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
        logger.info("Closing application...")
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
