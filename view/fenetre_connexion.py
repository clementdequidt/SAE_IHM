from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

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
        self.champMdp.setEchoMode(QLineEdit.EchoMode.Password)

        boutonConnexion = QPushButton("Se connecter")
        boutonConnexion.clicked.connect(self.verifierMdp)

        layout.addWidget(label)
        layout.addWidget(self.champMdp)
        layout.addWidget(boutonConnexion)

        self.setLayout(layout)

    def verifierMdp(self):
        if self.champMdp.text() == self.motDePasseAttendu:
            self.callbackConnexion()
            self.close()
        else:
            QMessageBox.critical(self, "Erreur", "Mot de passe incorrect.")