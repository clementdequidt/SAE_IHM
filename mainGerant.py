#Fichier crée par Bastien COUSIN, Pierre DELDALLE, Clément DEQUIDT, Sébastien GROUÉ
import sys
from PyQt6.QtWidgets import QApplication
from view.fenetreConnexion import FenetreConnexion
from controller.controllerApp import AppMultiPages

if __name__ == "__main__":
    app = QApplication(sys.argv)

    def lancerApplication():
        multiPages = AppMultiPages()
        multiPages.setWindowTitle("Application Gérant de Magasin")
        multiPages.resize(1280, 720)
        multiPages.show()

    fenetreConnexion = FenetreConnexion("SAE_Graphes", lancerApplication)
    fenetreConnexion.show()

    sys.exit(app.exec())