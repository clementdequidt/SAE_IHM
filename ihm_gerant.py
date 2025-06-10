import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QTextEdit, QDockWidget, QStackedWidget, QStatusBar, QFileDialog
)
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtCore import Qt

# --- Page de questionnaire ---
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QDateEdit
)
from PyQt6.QtCore import QDate

class PageQuestionnaire(QWidget):
    def __init__(self, switch_callback):
        super().__init__()
        self.switch_callback = switch_callback

        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>Questionnaire de démarrage</h2>"))

        self.projet_input= QLabel("Nom du projet")
        self.projet_input = QLineEdit()
        self.projet_input.setPlaceholderText("Saisissez le nom du projet")
        layout.addWidget(self.projet_input)

        self.auteur_input = QLineEdit()
        self.auteur_input.setPlaceholderText("Auteur du projet")
        layout.addWidget(self.auteur_input)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        layout.addWidget(QLabel("Date de création"))
        layout.addWidget(self.date_input)

        self.nom_magasin_input = QLineEdit()
        self.nom_magasin_input.setPlaceholderText("Nom du magasin")
        layout.addWidget(self.nom_magasin_input)

        self.adresse_magasin_input = QLineEdit()
        self.adresse_magasin_input.setPlaceholderText("Adresse du magasin")
        layout.addWidget(self.adresse_magasin_input)

        btn_valider = QPushButton("Valider")
        btn_valider.clicked.connect(self.verifier_et_passer)
        layout.addWidget(btn_valider)

        self.setLayout(layout)

    def verifier_et_passer(self):
        if not all([
            self.projet_input.text().strip(),
            self.auteur_input.text().strip(),
            self.nom_magasin_input.text().strip(),
            self.adresse_magasin_input.text().strip()
        ]):
            QMessageBox.warning(self, "Champs requis", "Veuillez remplir tous les champs.")
            return

        self.switch_callback()


# --- Fenêtre principale de l'application (ta classe existante) ---
class FenetreAppli(QMainWindow):
    def __init__(self, chemin: str = None):
        super().__init__()
        self.__chemin = chemin

        self.setWindowTitle("IHM Gérant")
        self.setWindowIcon(QIcon(sys.path[0] + '/icones/logo_but.png'))
        self.setGeometry(100, 100, 800, 600)

        # dock
        self.dock = QDockWidget('Liste de courses')
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        self.dock.setMaximumWidth(400)
        self.text_edit = QTextEdit()
        self.dock.setWidget(self.text_edit)

        # barre d'état
        self.barre_etat = QStatusBar()
        self.setStatusBar(self.barre_etat)
        self.barre_etat.showMessage("L'application est démarrée...", 2000)

        # barre de menu
        menu_bar = self.menuBar()
        menu_fichier = menu_bar.addMenu('&Fichier')
        menu_edition = menu_bar.addMenu('&Edition')
        menu_themes = menu_bar.addMenu("Affichage")

        action_clair = QAction("Thème clair", self)
        action_clair.triggered.connect(self.appliquer_theme_clair)
        action_sombre = QAction("Thème sombre", self)
        action_sombre.triggered.connect(self.appliquer_theme_sombre)

        menu_themes.addAction(action_clair)
        menu_themes.addAction(action_sombre)

        menu_fichier.addAction('Nouveau', self.nouveau)
        menu_fichier.addAction('Ouvrir', self.ouvrir)
        menu_fichier.addAction('Enregistrer', self.enregistrer)
        menu_fichier.addSeparator()
        menu_fichier.addAction('Quitter', self.close)

        action_annuler = QAction(QIcon(sys.path[0] + '/icones/left.png'), 'Précédent', self)
        action_annuler.setShortcut('Ctrl+Z')
        action_annuler.triggered.connect(self.text_edit.undo)
        menu_edition.addAction(action_annuler)

        action_retablir = QAction(QIcon(sys.path[0] + '/icones/right.png'), 'Rétablir', self)
        action_retablir.setShortcut('Ctrl+Y')
        action_retablir.triggered.connect(self.text_edit.redo)
        menu_edition.addAction(action_retablir)

    def appliquer_theme_clair(self):
        style_clair = """
            QWidget {
                background-color: #f0f0f0;
                color: #000000;
                font-family: Arial;
                font-size: 14px;
            }
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                padding: 5px;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #aaa;
            }
        """
        self.setStyleSheet(style_clair)

    def appliquer_theme_sombre(self):
        style_sombre = """
            QWidget {
                background-color: #2e2e2e;
                color: #ffffff;
                font-family: Arial;
                font-size: 14px;
            }
            QPushButton {
                background-color: #444;
                border: 1px solid #666;
                padding: 5px;
            }
            QLineEdit {
                background-color: #555;
                color: #ffffff;
                border: 1px solid #888;
            }
        """
        self.setStyleSheet(style_sombre)

    def nouveau(self):
        self.barre_etat.showMessage('Créer un nouveau ....', 2000)
        self.text_edit.clear()

    def ouvrir(self):
        self.barre_etat.showMessage('Ouvrir un fichier image....', 2000)
        chemin, _ = QFileDialog.getOpenFileName(directory=sys.path[0])
        if chemin:
            self.__chemin = chemin

    def enregistrer(self):
        self.barre_etat.showMessage('Enregistrer le texte....', 2000)
        chemin, _ = QFileDialog.getSaveFileName(directory=sys.path[0])
        if chemin:
            with open(chemin, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
            self.barre_etat.showMessage('Texte enregistré.', 2000)

# --- Gestionnaire de navigation entre pages ---
class AppMultiPages(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.page_questionnaire = PageQuestionnaire(self.lancer_appli)
        self.addWidget(self.page_questionnaire)  # index 0

        # La FenetreAppli sera ajoutée dynamiquement après validation
        self.setCurrentIndex(0)

    def lancer_appli(self):
        self.fenetre_appli = FenetreAppli()
        self.addWidget(self.fenetre_appli)  # index 1
        self.setCurrentIndex(1)
        self.fenetre_appli.showMaximized()

# --- Lancement de l'application ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    multi_pages = AppMultiPages()
    multi_pages.setWindowTitle("Application avec questionnaire")
    multi_pages.resize(1280, 720)
    multi_pages.show()
    sys.exit(app.exec())
