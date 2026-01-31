from src.Presentation.presentation import AppUI

from src.Domain.controller import Controller

from src.Persistance.gps_client import GpsPoll

if __name__ == "__main__":
    gps_thread = GpsPoll()
    gps_thread.start()

    controller = Controller(gps_client=gps_thread)

    app = AppUI(controller, gps_thread)

    try:
        app.mainloop()
    except KeyboardInterrupt:
        print("Closing application...")
        app.close_app()
    except Exception as e:
        print(f"Unexpected error: {e}")