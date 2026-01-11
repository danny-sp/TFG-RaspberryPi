from src.Presentation.presentation import AppUI

from src.Domain.controller import Controller

from src.Persistance.gps_client import GpsPoll

def main():
    print("Iniciando Sistema TFG...")

    gps_thread = GpsPoll()
    gps_thread.start()

    controller = Controller(gps_client=gps_thread)

    app = AppUI(controller)
    app.mainloop()

if __name__ == "__main__":
    main()