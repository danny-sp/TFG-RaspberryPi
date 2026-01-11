from src.Domain.controller import ChargeController
from src.Presentation.presentation import AppUI

def main():
    print("Iniciando Sistema TFG...")

    controller = ChargeController(mqtt)

    app = AppUI(controller)
    app.mainloop()

if __name__ == "__main__":
    main()