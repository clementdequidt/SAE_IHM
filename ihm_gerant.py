import sys
import platform
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QMessageBox, QTextEdit, QDockWidget, QStackedWidget, QStatusBar, QFileDialog, QDateEdit, QScrollArea, QCheckBox, QListWidget, QListWidgetItem
)
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QIcon, QDrag, QMouseEvent
from PyQt6.QtCore import Qt, QDate

# --- Détection du thème système ---
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

            # Appliquer une belle feuille de style
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit, QDateEdit {
                border: 1px solid;
                border-radius: 5px;
                margin-bottom: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005999;
            }
        """)
    
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
        self.switch_callback()  # Cette fonction ouvrira la fenêtre ChoisirProduits
        
# --- Choisir les produits disponibles dans le magasin ---
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QScrollArea, QMessageBox

class ChoisirProduits(QWidget):
    def __init__(self, fichier_produits='liste_produits.json'):
        super().__init__()
        self.setWindowTitle("Choisir les produits disponibles")
        self.setGeometry(100, 100, 600, 500)

        self.fichier_produits = fichier_produits
        self.produits_par_categorie = {}
        self.categories = []
        self.page_courante = 0
        self.categories_par_page = 3
        self.listes_categorie = {}

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        titre = QLabel("Sélectionnez les produits disponibles :")
        titre.setObjectName("titrePrincipal")
        self.layout.addWidget(titre)

        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)

        self.container = QWidget()
        self.scroll.setWidget(self.container)
        self.container_layout = QHBoxLayout()
        self.container.setLayout(self.container_layout)

        # Navigation boutons
        nav_layout = QHBoxLayout()
        self.btn_precedent = QPushButton("Page Précédente")
        self.btn_precedent.clicked.connect(self.page_precedente)
        nav_layout.addWidget(self.btn_precedent)
        self.btn_suivant = QPushButton("Page Suivante")
        self.btn_suivant.clicked.connect(self.page_suivante)
        nav_layout.addWidget(self.btn_suivant)
        self.layout.addLayout(nav_layout)

        self.btn_valider = QPushButton("Valider la sélection")
        self.btn_valider.clicked.connect(self.valider_selection)
        self.layout.addWidget(self.btn_valider)

        self.charger_produits()

    def charger_produits(self):
        try:
            with open(self.fichier_produits, 'r', encoding='utf-8') as f:
                self.produits_par_categorie = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger la liste des produits:\n{e}")
            self.produits_par_categorie = {}

        self.categories = list(self.produits_par_categorie.keys())
        self.page_courante = 0
        self.afficher_page()
        
        self.setStyleSheet("""
            QLabel#titrePrincipal {
                font-size: 16px;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
            }

            QLabel#categorieLabel {
                font-weight: bold;
                font-size: 13px;
            }

            QListWidget {
                border: 1px solid gray;
                border-radius: 5px;
                padding: 5px;
            }

            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #005999;
            }
        """)


    def afficher_page(self):
        # Vider l'affichage actuel et la liste des widgets
        for i in reversed(range(self.container_layout.count())):
            layout_or_widget = self.container_layout.itemAt(i)
            if layout_or_widget is not None:
                widget = layout_or_widget.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    # Si c'est un layout
                    layout = layout_or_widget.layout()
                    if layout is not None:
                        self._clear_layout(layout)
                        self.container_layout.removeItem(layout)
                    else:
                        self.container_layout.removeItem(layout_or_widget)

        self.listes_categorie = {}

        # Obtenir les catégories à afficher pour la page courante
        start = self.page_courante * self.categories_par_page
        end = start + self.categories_par_page
        categories_a_afficher = self.categories[start:end]

        for categorie in categories_a_afficher:
            produits = self.produits_par_categorie[categorie]
            layout_categorie = QVBoxLayout()
            
            label = QLabel(categorie)
            label.setObjectName("categorieLabel")
            layout_categorie.addWidget(label)

            liste_widget = QListWidget()
            liste_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
            for produit in produits:
                item = QListWidgetItem(produit)
                liste_widget.addItem(item)
            layout_categorie.addWidget(liste_widget)

            self.container_layout.addLayout(layout_categorie)
            self.listes_categorie[categorie] = liste_widget

        # Mettre à jour état des boutons
        self.btn_precedent.setEnabled(self.page_courante > 0)
        self.btn_suivant.setEnabled(end < len(self.categories))

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self._clear_layout(child_layout)

    def page_precedente(self):
        if self.page_courante > 0:
            self.page_courante -= 1
            self.afficher_page()

    def page_suivante(self):
        if (self.page_courante + 1) * self.categories_par_page < len(self.categories):
            self.page_courante += 1
            self.afficher_page()

    def valider_selection(self):
        selection_finale = {}
        total_selectionnes = 0

        for categorie, liste_widget in self.listes_categorie.items():
            produits_choisis = [item.text() for item in liste_widget.selectedItems()]
            if produits_choisis:
                selection_finale[categorie] = produits_choisis
                total_selectionnes += len(produits_choisis)

        if total_selectionnes < 20:
            QMessageBox.warning(
                self, 
                "Sélection insuffisante", 
                f"Veuillez choisir au moins 20 produits (actuellement : {total_selectionnes})."
            )
            return
        
        self.close()
        
# --- Fenêtre principale de l'application ---
class FenetreAppli(QMainWindow):
    def __init__(self, chemin: str = None):
        super().__init__()
        self.__chemin = chemin

        self.setWindowTitle("IHM Gérant")
        self.setGeometry(100, 100, 1000, 700)

        # Barre d'état
        self.barre_etat = QStatusBar()
        self.setStatusBar(self.barre_etat)
        self.barre_etat.showMessage("L'application est démarrée...", 2000)

        # Plan du magasin (QLabel avec image)
        self.label_plan = QLabel()
        self.label_plan.setPixmap(QPixmap("Quadrillage_Final.jpg"))
        self.label_plan.setScaledContents(True)
        self.label_plan.setAcceptDrops(True)
        self.label_plan.setMinimumSize(600, 600)

        # Liste des produits (draggable)
        self.liste_produits = QListWidget()
        self.liste_produits.setDragEnabled(True)
        self.liste_produits.setFixedWidth(300)
        for produit in ["Lait", "Pain", "Pâtes", "Riz", "Beurre"]:  # Tu remplaceras ça par ta vraie liste
            self.liste_produits.addItem(produit)

        # Splitter horizontal : plan à gauche, liste à droite
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.label_plan)
        self.splitter.addWidget(self.liste_produits)
        self.setCentralWidget(self.splitter)

        # Menu (thèmes, etc.)
        self.creer_menu()

        # Drag & drop événements sur le plan
        self.label_plan.dragEnterEvent = self.dragEnterEvent
        self.label_plan.dropEvent = self.dropEvent

    def creer_menu(self):
        menu_bar = self.menuBar()
        menu_fichier = menu_bar.addMenu('&Fichier')

        menu_fichier.addAction('Nouveau', self.nouveau)
        menu_fichier.addAction('Ouvrir', self.ouvrir)
        menu_fichier.addAction('Enregistrer', self.enregistrer)
        menu_fichier.addSeparator()
        menu_fichier.addAction('Quitter', self.close)

    def nouveau(self):
        self.barre_etat.showMessage('Créer un nouveau fichier...', 2000)
        self.liste_produits.clear()

    def ouvrir(self):
        chemin, _ = QFileDialog.getOpenFileName(directory=sys.path[0])
        if chemin:
            self.__chemin = chemin
            self.barre_etat.showMessage(f'Fichier ouvert : {chemin}', 2000)

    def enregistrer(self):
        chemin, _ = QFileDialog.getSaveFileName(directory=sys.path[0])
        if chemin:
            with open(chemin, 'w', encoding='utf-8') as f:
                for i in range(self.liste_produits.count()):
                    f.write(self.liste_produits.item(i).text() + '\n')
            self.barre_etat.showMessage('Liste enregistrée.', 2000)

    # Gestion du drag & drop
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        position = event.position().toPoint()
        texte = event.mimeData().text()

        label = QLabel(texte, self.label_plan)
        label.move(position)
        label.setStyleSheet("background-color: rgba(255,255,255,200); border: 1px solid black; padding: 2px;")
        label.show()
        label.raise_()

        event.acceptProposedAction()

# --- Gestionnaire de navigation entre pages ---
class AppMultiPages(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.page_questionnaire = PageQuestionnaire(self.aller_a_choisir_produits)
        self.addWidget(self.page_questionnaire)  # index 0

        # La FenetreAppli sera ajoutée dynamiquement après validation
        self.setCurrentIndex(0)

    def aller_a_choisir_produits(self):
        self.choisir_produits = ChoisirProduits()
        self.addWidget(self.choisir_produits)  # index 1
        self.setCurrentIndex(1)
        self.choisir_produits.showMaximized()
        
    def aller_a_fenetre_appli(self):
        self.fenetre_appli = FenetreAppli()
        self.addWidget(self.fenetre_appli)  # index 2
        self.setCurrentIndex(2)
        self.fenetre_appli.showMaximized()

# --- Lancement de l'application ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    multi_pages = AppMultiPages()
    multi_pages.setWindowTitle("Application avec questionnaire")
    multi_pages.resize(1280, 720)
    multi_pages.show()
    sys.exit(app.exec())
