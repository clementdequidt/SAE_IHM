import sys
import platform
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QMessageBox, QTextEdit, QDockWidget, QStackedWidget, QStatusBar, QFileDialog, QDateEdit, QScrollArea, QCheckBox, QListWidget, QListWidgetItem,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsTextItem
)
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QIcon, QDrag, QMouseEvent, QWheelEvent, QPainter, QBrush, QColor, QFont, QDragMoveEvent
from PyQt6.QtCore import Qt, QDate, QPointF, QRectF, pyqtSignal, QMimeData


#Fonction pour détecter le système d'exploitation du client
def detecter_theme_systeme():
    if platform.system() == "Windows":
        try:
            import winreg #importation de winreg pour lire, écrire et modifier le registre de Windows
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key_path = r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize'
            key = winreg.OpenKey(registry, key_path)
            apps_use_light_theme, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
            return "clair" if apps_use_light_theme == 1 else "sombre"
        except Exception:
            return "clair"
    return "clair"
#Si le système d'exploitation est différents de windows la couleur est de base blanche

# --- Page de questionnaire ---
class PageQuestionnaire(QWidget):
    def __init__(self, switch_callback):
        super().__init__()
        self.switch_callback = switch_callback

        form_layout = QVBoxLayout() #layout vertical pour structurer le questionnaire
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(15) #Espacement de 15 entre chaque layout

        title = QLabel("Création d'un nouveau magasin") #Label pour préciser ce que l'on fais
        title.setStyleSheet("font-size: 24px; font-weight: bold;") #Police utilisé, caractère, taille et mise en gras
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(title)

        self.projet_input = self._add_labeled_input("Nom du projet :", "Saisissez le nom du projet", form_layout) #Ajout d'un label pour saisir le nom du projet
        self.auteur_input = self._add_labeled_input("Votre nom :", "Saisissez votre nom", form_layout) #Ajout d'un label pour saisir notre nom 

        form_layout.addWidget(QLabel("Date de création :")) #Ajout d'un label pour préciser que l'on doit mettre la date de création
        self.date_input = QDateEdit() #Un input QDateEdit pour ajouter la date de création du magasin
        self.date_input.setCalendarPopup(True) #Apparition d'un calendrier pour faciliter l'utilisateur
        self.date_input.setDate(QDate.currentDate()) #Quand on crée un nouveau magasin la date actuelle ou l'on lance l'appli apparait
        form_layout.addWidget(self.date_input)

        self.nom_magasin_input = self._add_labeled_input("Nom du magasin :", "Nom du magasin", form_layout) #Ajout d'un label pour saisir le nom du magasin
        self.adresse_magasin_input = self._add_labeled_input("Adresse du magasin :", "Adresse complète", form_layout) #Ajout d'un label pour saisir l'adresse du magasin

        btn_valider = QPushButton("Valider") #Un bouton pour valider
        btn_valider.clicked.connect(self.verifier_et_passer) #Appel d'une fonction, si tout les champs
        #sont complé alors on peut passer sinon on ne peut pas valider
        form_layout.addWidget(btn_valider)

        outer_layout = QVBoxLayout() #Ajout d'un layout vertical
        outer_layout.addStretch()
        outer_layout.addLayout(form_layout)
        outer_layout.addStretch()
        self.setLayout(outer_layout)
        
        #On définit la taille de police des label, des lineEdit,DateEdit et des Bouttons
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
    #Si tout les champs ne sont pas vérifier et rempli alors on renvoie un warning pour dire que les champs sont nécessaires
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
        
#Choisir les produits disponibles dans le magasin
class ChoisirProduits(QWidget):
    selection_validee = pyqtSignal(dict) 

    def __init__(self, fichier_produits='liste_produits.json'): #Appelle de la liste de produits (la même que celle donner par le prof)
        super().__init__()
        self.setWindowTitle("Choisir les produits disponibles")
        self.setGeometry(100, 100, 600, 500)

        self.fichier_produits = fichier_produits
        self.produits_par_categorie = {}
        self.categories = [] #Liste pour les catégories d'aliments
        self.page_courante = 0
        self.categories_par_page = 3 # Un nombre de 3 catégorie par page de l'application
        self.listes_categorie = {} # Contient les QListWidget actuellement affichés
        
        #Dictionnaire pour stocker toutes les sélections (produit -> est_sélectionné)
        self.selections_globales = {} 

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        titre = QLabel("Sélectionnez les produits disponibles :")
        titre.setObjectName("titrePrincipal")
        self.layout.addWidget(titre)

        self.scroll = QScrollArea()#Pouvoir sélectionner les produits en scrollant
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)

        self.container = QWidget()
        self.scroll.setWidget(self.container)
        self.container_layout = QHBoxLayout()
        self.container.setLayout(self.container_layout)

        nav_layout = QHBoxLayout()
        self.btn_precedent = QPushButton("Page Précédente") #Boutton précédent pour aller dans la page d'avant
        self.btn_precedent.clicked.connect(self.page_precedente)
        nav_layout.addWidget(self.btn_precedent)
        self.btn_suivant = QPushButton("Page Suivante")  #Boutton suivant pour aller dans la page d'après
        self.btn_suivant.clicked.connect(self.page_suivante)
        nav_layout.addWidget(self.btn_suivant)
        self.layout.addLayout(nav_layout)

        self.btn_valider = QPushButton("Valider la sélection") #Boutton pour valider la sélection de produits
        self.btn_valider.clicked.connect(self.valider_selection)
        self.layout.addWidget(self.btn_valider)

        self.charger_produits()
        
    #Fonction pour charger les produits
    def charger_produits(self):
        try:
            with open(self.fichier_produits, 'r', encoding='utf-8') as f:
                self.produits_par_categorie = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger la liste des produits:\n{e}")
            self.produits_par_categorie = {}
        
        #Initialiser selections_globales avec tous les produits non sélectionnés au départ
        for categorie, produits in self.produits_par_categorie.items():
            for produit in produits:
                self.selections_globales[produit] = False

        self.categories = list(self.produits_par_categorie.keys())
        self.page_courante = 0
        self.afficher_page()
        
        #On définit la taille de police des label, des listWidget et des Bouttons
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

    def _sauvegarder_selections_courantes(self):
        """Sauvegarde l'état des QListWidget actuellement affichés dans selections_globales."""
        for categorie, liste_widget in self.listes_categorie.items():
            for i in range(liste_widget.count()):
                item = liste_widget.item(i)
                self.selections_globales[item.text()] = item.isSelected()

    def afficher_page(self):
        #Sauvegarder les sélections AVANT de vider les listes
        self._sauvegarder_selections_courantes()

        # Nettoyage des widgets précédents
        for i in reversed(range(self.container_layout.count())):
            layout_or_widget = self.container_layout.itemAt(i)
            if layout_or_widget is not None:
                widget = layout_or_widget.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    layout = layout_or_widget.layout()
                    if layout is not None:
                        self._clear_layout(layout)
                        self.container_layout.removeItem(layout)
                    else:
                        self.container_layout.removeItem(layout_or_widget)

        self.listes_categorie = {} # Réinitialise pour les nouvelles listes

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
                #Restaurer la sélection de l'item si elle était sauvegardée
                if self.selections_globales.get(produit, False): # Par défaut à False si pas trouvé
                    item.setSelected(True)
                liste_widget.addItem(item)
            layout_categorie.addWidget(liste_widget)

            self.container_layout.addLayout(layout_categorie)
            self.listes_categorie[categorie] = liste_widget

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
        #Sauvegarder les sélections avant de changer de page
        self._sauvegarder_selections_courantes()
        if self.page_courante > 0:
            self.page_courante -= 1
            self.afficher_page()

    def page_suivante(self):
        #Sauvegarder les sélections avant de changer de page
        self._sauvegarder_selections_courantes()
        if (self.page_courante + 1) * self.categories_par_page < len(self.categories):
            self.page_courante += 1
            self.afficher_page()

    def valider_selection(self):
        #S'assurer que les sélections de la page actuelle sont sauvegardées avant validation
        self._sauvegarder_selections_courantes() 
        
        selection_finale = {}
        total_selectionnes = 0

        # Parcourir les sélections_globales pour construire la selection_finale
        for produit, selected in self.selections_globales.items():
            if selected:
                # Retrouver la catégorie du produit pour le classer
                for categorie, produits_liste in self.produits_par_categorie.items():
                    if produit in produits_liste:
                        if categorie not in selection_finale:
                            selection_finale[categorie] = []
                        selection_finale[categorie].append(produit)
                        total_selectionnes += 1
                        break # Produit trouvé, passer au suivant

        #Si le nombre de produit est inférieur a 20 alors message d'erreur pour nous dire qu'il faut un minima de 20 produits
        if total_selectionnes < 20:
            QMessageBox.warning(
                self, 
                "Sélection insuffisante", 
                f"Veuillez choisir au moins 20 produits (actuellement : {total_selectionnes})."
            )
            return
        
        self.selection_validee.emit(selection_finale) 
        self.close()
        
class Image(QGraphicsView):
    produit_place_signal = pyqtSignal(str, QPointF) 

    def __init__(self, chemin: str):
        super().__init__()

        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._pixmap_item = QGraphicsPixmapItem()
        self._scene.addItem(self._pixmap_item)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        self.setAcceptDrops(True)

        pixmap = QPixmap(chemin)
        if pixmap.isNull():
            label = QLabel(f"Image non trouvée : {chemin}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._scene.addWidget(label)
        else:
            self.setPixmap(pixmap)

    def setPixmap(self, pixmap: QPixmap):
        self._zoom = 0
        self._pixmap_item.setPixmap(pixmap)
        self._scene.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._empty = False

    def wheelEvent(self, event: QWheelEvent):
        if self._empty:
            return

        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
            self._zoom += 1
        else:
            zoom_factor = zoom_out_factor
            self._zoom -= 1

        if self._zoom < -10:
            self._zoom = -10
            return
        if self._zoom > 30:
            self._zoom = 30
            return

        self.scale(zoom_factor, zoom_factor)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasText():
            product_name = event.mimeData().text()
            scene_pos = self.mapToScene(event.position().toPoint())

            text_item = QGraphicsTextItem(product_name)
            text_item.setDefaultTextColor(QColor("red"))
            text_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            
            text_item.setPos(scene_pos.x() - text_item.boundingRect().width() / 2,
                             scene_pos.y() - text_item.boundingRect().height() / 2)
            
            self._scene.addItem(text_item)
            event.acceptProposedAction()

            self.produit_place_signal.emit(product_name, scene_pos)
        else:
            event.ignore()

class FenetreAppli(QMainWindow):
    def __init__(self, chemin: str = None, produits_selectionnes: dict = None):
        super().__init__()
        self.__chemin = chemin
        self.produits_selectionnes = produits_selectionnes if produits_selectionnes is not None else {}
        self.positions_produits = {} 
        
        self.setWindowTitle("test_ihm_client")
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen_geometry)

        self.image_viewer = Image(self.__chemin)
        self.setCentralWidget(self.image_viewer)
        self.image_viewer.produit_place_signal.connect(self.enregistrer_position_produit)

        self.dock = QDockWidget('Produits à placer')
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        self.dock.setMaximumWidth(400)
        
        self.liste_produits_dock = QListWidget() 
        self.dock.setWidget(self.liste_produits_dock)
        
        self.liste_produits_dock.setDragEnabled(True)
        self.liste_produits_dock.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        self.liste_produits_dock.setDefaultDropAction(Qt.DropAction.MoveAction)
        
        self.afficher_produits_dans_dock() 

        self.barre_etat = QStatusBar()
        self.setStatusBar(self.barre_etat)
        self.barre_etat.showMessage("L'application est démarrée...", 2000)

        menu_bar = self.menuBar()
        menu_fichier = menu_bar.addMenu('&Fichier')
        menu_edition = menu_bar.addMenu('&Edition')
        menu_aide = menu_bar.addMenu('&Aide')

        menu_fichier.addAction('Nouveau', self.nouveau)
        menu_fichier.addAction('Ouvrir', self.ouvrir)
        menu_fichier.addAction('Enregistrer les positions', self.enregistrer_positions) 
        menu_fichier.addSeparator()
        menu_fichier.addAction('Quitter', self.destroy)

    def afficher_produits_dans_dock(self):
        """Affiche les produits sélectionnés dans le QListWidget du dock et les rend glissables."""
        self.liste_produits_dock.clear()
        if not self.produits_selectionnes:
            item = QListWidgetItem("Aucun produit sélectionné.")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.liste_produits_dock.addItem(item)
            return

        for categorie, produits in self.produits_selectionnes.items():
            category_item = QListWidgetItem(f"--- {categorie} ---")
            category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsDragEnabled)
            category_item.setForeground(QBrush(QColor("blue")))
            self.liste_produits_dock.addItem(category_item)

            for produit in produits:
                item = QListWidgetItem(produit)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled) 
                self.liste_produits_dock.addItem(item)

    def enregistrer_position_produit(self, product_name: str, position: QPointF):
        """Reçoit le signal d'un produit placé et enregistre sa position."""
        self.positions_produits[product_name] = {'x': position.x(), 'y': position.y()}
        self.barre_etat.showMessage(f"Produit '{product_name}' placé à ({position.x():.0f}, {position.y():.0f})", 3000)
        print(f"Positions actuelles: {self.positions_produits}")

    def enregistrer_positions(self):
        """Sauvegarde les positions des produits dans un fichier JSON."""
        if not self.positions_produits:
            QMessageBox.information(self, "Enregistrer les positions", "Aucun produit n'a été placé pour être enregistré.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer les positions des produits", 
                                                   "positions_produits.json", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    serializable_positions = {
                        name: {'x': pos['x'], 'y': pos['y']} 
                        for name, pos in self.positions_produits.items()
                    }
                    json.dump(serializable_positions, f, indent=4, ensure_ascii=False)
                self.barre_etat.showMessage(f"Positions enregistrées dans {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'enregistrement", f"Impossible d'enregistrer les positions:\n{e}")

    def nouveau(self):
        self.barre_etat.showMessage('Créer un nouveau ....', 2000)
        boite = QFileDialog()
        chemin, validation = boite.getOpenFileName(directory = sys.path[0])
        if validation:
            self.__chemin = chemin
            self.image_viewer.setPixmap(QPixmap(self.__chemin))
            self.positions_produits = {}
            self.image_viewer._scene.clear()
            self.image_viewer._scene.addItem(self.image_viewer._pixmap_item)
            self.barre_etat.showMessage('Nouveau plan chargé.', 2000)

    def ouvrir(self):
        self.barre_etat.showMessage('Ouvrir un nouveau....', 2000)
        boite = QFileDialog()
        chemin, validation = boite.getOpenFileName(self, "Ouvrir une image de plan", directory = sys.path[0], filter="Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if validation:
            self.__chemin = chemin
            self.image_viewer.setPixmap(QPixmap(self.__chemin))
            self.positions_produits = {}
            self.image_viewer._scene.clear()
            self.image_viewer._scene.addItem(self.image_viewer._pixmap_item)
            self.barre_etat.showMessage(f"Plan chargé: {self.__chemin}", 2000)

    def enregistrer(self):
        self.barre_etat.showMessage('Enregistrer....', 2000 )
        QMessageBox.information(self, "Enregistrer le projet", "La fonction d'enregistrement global du projet n'est pas encore implémentée. Utilisez 'Enregistrer les positions' pour les emplacements des produits.")

    def affiche_image(self):
        pass 

# --- Gestionnaire de navigation entre pages ---
class AppMultiPages(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.page_questionnaire = PageQuestionnaire(self.aller_a_choisir_produits)
        self.addWidget(self.page_questionnaire)  # index 0

        self.choisir_produits = ChoisirProduits()
        self.choisir_produits.selection_validee.connect(self.aller_a_fenetre_appli) 
        self.addWidget(self.choisir_produits) # index 1

        self.fenetre_appli = None 

        self.setCurrentIndex(0)

    def aller_a_choisir_produits(self):
        self.setCurrentIndex(1)

    def aller_a_fenetre_appli(self, produits_selectionnes: dict): 
        chemin_image = sys.path[0] + '/Quadrillage_Final.jpg'
        
        if self.fenetre_appli is None:
            self.fenetre_appli = FenetreAppli(chemin=chemin_image, produits_selectionnes=produits_selectionnes) 
            self.addWidget(self.fenetre_appli)  # index 2
        else:
            self.fenetre_appli.produits_selectionnes = produits_selectionnes
            self.fenetre_appli.afficher_produits_dans_dock() 
            
        self.setCurrentIndex(2)

# --- Lancement de l'application ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    multi_pages = AppMultiPages()
    multi_pages.setWindowTitle("Application avec questionnaire")
    multi_pages.resize(1280, 720)
    multi_pages.show()
    sys.exit(app.exec())