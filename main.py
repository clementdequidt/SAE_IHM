# main.py
import sys
from PyQt6.QtWidgets import QApplication
from MVC_MODEL import ModeleMagasin
from MVC_VIEW import FenetreAppliVue
from MVC_CONTROLLER import ControleurMagasin

if __name__ == "__main__":
    app = QApplication(sys.argv)

    modele = ModeleMagasin()
    vue = FenetreAppliVue()
    controleur = ControleurMagasin(modele, vue)

    vue.show()
    sys.exit(app.exec())