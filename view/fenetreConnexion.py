#Fichier crée par Bastien COUSIN, Pierre DELDALLE, Clément DEQUIDT, Sébastien GROUÉ
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

#Mise en place d'un mot de passe pour accéder à l'application gérant
class FenetreConnexion(QWidget):
    def __init__(self, motDePasseAttendu, callbackConnexion):
        super().__init__()
        self.motDePasseAttendu = motDePasseAttendu
        self.callbackConnexion = callbackConnexion

        self.setWindowTitle("Connexion")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        label = QLabel("Entrez le mot de passe :")
        self.champMdp = QLineEdit()
        self.champMdp.setEchoMode(QLineEdit.EchoMode.Password) #Cache le mot de passe entré

        boutonConnexion = QPushButton("Se connecter")
        boutonConnexion.clicked.connect(self.verifierMdp) #Pour vérifier si le mot de passe est correct

        layout.addWidget(label)
        layout.addWidget(self.champMdp)
        layout.addWidget(boutonConnexion)

        self.setLayout(layout)

    #Fonction qui permet de vérifier si le mot de passe entré est correct ou non
    def verifierMdp(self):
        if self.champMdp.text() == self.motDePasseAttendu:
            self.callbackConnexion()
            self.close() #si mot de passe correct, on ferme la fenêtre de connexion et on lance la "vraie" application
        else:
            QMessageBox.critical(self, "Erreur", "Mot de passe incorrect.") #mot de passe incorrect, message d'erreur + faut recommencer