import sys
import platform
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QTextEdit, QDockWidget, QStackedWidget, QStatusBar, QFileDialog, QDateEdit
)
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtCore import Qt, QDate

# --- Détection du thème système (Windows uniquement pour l'instant) ---
def detecter_theme_systeme():
    if platform.system() == "Windows":
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key_path = r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize'
            key = winreg.OpenKey(registry, key_path)
            apps_use_light_theme, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
            return "clair" if apps_use_light_theme == 1 else "sombre"
        except Exception:
            return "clair"  # Par défaut si erreur
    return "clair"  # Par défaut sur Linux/macOS

# --- Page de questionnaire ---
class PageQuestionnaire(QWidget):
    def __init__(self, switch_callback):
        super().__init__()
        self.switch_callback = switch_callback

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(15)

        title = QLabel("Création d'un nouveau magasin")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(title)

        # Exemple champ stylisé
        self.projet_input = self._add_labeled_input("Nom du projet :", "Saisissez le nom du projet", form_layout)
        self.auteur_input = self._add_labeled_input("Votre nom :", "Saisissez votre nom", form_layout)

        form_layout.addWidget(QLabel("Date de création :"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addWidget(self.date_input)

        self.nom_magasin_input = self._add_labeled_input("Nom du magasin :", "Nom du magasin", form_layout)
        self.adresse_magasin_input = self._add_labeled_input("Adresse du magasin :", "Adresse complète", form_layout)

        btn_valider = QPushButton("Valider")
        btn_valider.clicked.connect(self.verifier_et_passer)
        form_layout.addWidget(btn_valider)

        # Centrage vertical
        outer_layout = QVBoxLayout()
        outer_layout.addStretch()
        outer_layout.addLayout(form_layout)
        outer_layout.addStretch()
        self.setLayout(outer_layout)

    def _add_labeled_input(self, label_text, placeholder, layout):
        layout.addWidget(QLabel(label_text))
        line = QLineEdit()
        line.setPlaceholderText(placeholder)
        layout.addWidget(line)
        return line

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

# --- Fenêtre principale de l'application ---
class FenetreAppli(QMainWindow):
    def __init__(self, chemin: str = None):
        super().__init__()
        self.__chemin = chemin

        self.setWindowTitle("IHM Gérant")
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

        # Appliquer le thème système automatiquement au lancement
        self.appliquer_theme_par_defaut()

    def get_stylesheet(self, theme: str) -> str:
        if theme == "clair":
            return """
                QWidget {
                    background-color: #f0f0f0;
                    color: #000;
                    font-family: Arial;
                    font-size: 14px;
                    }
                QLabel {
                    color: #000;
                    }
                QLineEdit, QDateEdit {
                    background-color: #fff;
                    color: #000;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 4px;
                    }
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    }
                QPushButton:hover {
                    background-color: #005999;
                    }
            """
        else:
            return """
                QWidget {
                    background-color: #2e2e2e;
                    color: #fff;
                    font-family: Arial;
                    font-size: 14px;
                    }
                QLabel {
                    color: #fff;
                    }
                QLineEdit, QDateEdit {
                    background-color: #444;
                    color: #fff;
                    border: 1px solid #666;
                    border-radius: 4px;
                    padding: 4px;
                    }
                QPushButton {
                    background-color: #3a7bd5;
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    }
                QPushButton:hover {
                    background-color: #285ea8;
                    }
            """

    def appliquer_theme_clair(self):
        self.setStyleSheet(self.get_stylesheet("clair"))

    def appliquer_theme_sombre(self):
        self.setStyleSheet(self.get_stylesheet("sombre"))

    def appliquer_theme_par_defaut(self):
        theme = detecter_theme_systeme()
        self.setStyleSheet(self.get_stylesheet(theme))

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
