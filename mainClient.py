# main.py
import sys
from PyQt6.QtWidgets import QApplication
from mvcModeleClient import ModeleMagasin
from mvcVueClient import FenetreAppliVue
from mvcContollerClient import ControleurMagasin

if __name__ == "__main__":
    app = QApplication(sys.argv)

    modele = ModeleMagasin()
    vue = FenetreAppliVue()
    controleur = ControleurMagasin(modele, vue)

    vue.show()
    sys.exit(app.exec())