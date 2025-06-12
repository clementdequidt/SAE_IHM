# main.py
import sys
from PyQt6.QtWidgets import QApplication
from MVC_MODEL import StoreModel
from MVC_VIEW import FenetreAppliView
from MVC_CONTROLLER import StoreController

if __name__ == "__main__":
    app = QApplication(sys.argv)

    model = StoreModel()
    view = FenetreAppliView()
    controller = StoreController(model, view)

    view.show()
    sys.exit(app.exec())