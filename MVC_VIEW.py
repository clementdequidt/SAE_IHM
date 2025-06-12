# MVC_VIEW.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QStatusBar,
    QLabel, QFileDialog, QDockWidget, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QWidget,
    QListWidget, QPushButton, QHBoxLayout, QMessageBox, QListWidgetItem
)
from PyQt6.QtGui import QPixmap, QWheelEvent, QPainter, QFont, QColor
from PyQt6.QtCore import Qt, QPointF, QRectF, QCoreApplication


# --- Widget d'Affichage d'Image (QGraphicsView pour afficher la carte et les produits) ---
class VueImage(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._zoom = 0
        self._est_vide = True
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._element_pixmap = QGraphicsPixmapItem()
        self._scene.addItem(self._element_pixmap)

        self._elements_texte_produit = {} # Pour stocker les QGraphicsTextItem pour chaque produit

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    def definirPixmapCarte(self, pixmap: QPixmap):
        """Définit le pixmap d'arrière-plan pour la scène."""
        self._zoom = 0
        self._element_pixmap.setPixmap(pixmap)
        self._scene.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._est_vide = False
        self._element_pixmap.setZValue(0) # S'assurer que le pixmap est en bas de la valeur Z

    def placerEtiquetteProduit(self, nom_produit: str, x: float, y: float):
        """
        Place une étiquette de produit sur la carte aux coordonnées de scène données.
        Supprime l'étiquette existante pour le même produit si présente.
        """
        # Supprimer l'étiquette existante pour ce produit si elle est déjà sur la carte
        if nom_produit in self._elements_texte_produit:
            self._scene.removeItem(self._elements_texte_produit[nom_produit])
            del self._elements_texte_produit[nom_produit]

        # Créer un nouvel élément de texte pour le produit
        element_texte = self._scene.addText(nom_produit)
        element_texte.setDefaultTextColor(QColor("red")) # Les produits seront rouges pour les clients
        element_texte.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        # Positionner l'élément de texte de manière à ce que son centre soit à (x, y)
        element_texte.setPos(x - element_texte.boundingRect().width() / 2,
                             y - element_texte.boundingRect().height() / 2)

        element_texte.setZValue(1) # S'assurer que les étiquettes de produit sont au-dessus de la carte
        self._elements_texte_produit[nom_produit] = element_texte

    def effacerToutesEtiquettesProduit(self):
        """Supprime toutes les étiquettes de produit actuellement affichées sur la carte."""
        for item in list(self._elements_texte_produit.values()):
            self._scene.removeItem(item)
        self._elements_texte_produit.clear()

    def wheelEvent(self, event: QWheelEvent):
        """Gère les événements de la molette de la souris pour le zoom."""
        if self._est_vide:
            return

        facteur_zoom_avant = 1.25
        facteur_zoom_arriere = 1 / facteur_zoom_avant

        if event.angleDelta().y() > 0:
            facteur_zoom = facteur_zoom_avant
            self._zoom += 1
        else:
            facteur_zoom = facteur_zoom_arriere
            self._zoom -= 1

        # Empêcher le zoom excessif
        if self._zoom < -10:
            self._zoom = -10
            return
        if self._zoom > 30:
            self._zoom = 30
            return

        self.scale(facteur_zoom, facteur_zoom)


# --- Fenêtre principale de l'application ---
class FenetreAppliVue(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application Client de Magasin")
        geometrie_ecran = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(geometrie_ecran)

        self.configurerUI()
        self.appliquerStyles()
        self.showMaximized()

    def configurerUI(self):
        # --- Barre supérieure pour les informations du magasin ---
        self.barre_superieure_toolbar = QToolBar("Informations du Magasin")
        self.barre_superieure_toolbar.setMovable(False)
        self.barre_superieure_toolbar.toggleViewAction().setVisible(False)
        
        self.widget_barre_superieure = QWidget()
        self.layout_barre_superieure = QHBoxLayout(self.widget_barre_superieure)
        self.widget_barre_superieure.setFixedHeight(90)
        self.widget_barre_superieure.setStyleSheet("background-color: #f0f0f0;")

        self.layout_pile_info = QVBoxLayout()
        self.layout_pile_info.setContentsMargins(0, 0, 0, 0)
        self.layout_pile_info.setSpacing(2)

        self.etiquette_nom_magasin = QLabel("Magasin : Aucun plan chargé")
        self.etiquette_nom_magasin.setStyleSheet("font-size: 20px; font-weight: bold; color: #005999;")
        self.etiquette_nom_magasin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_pile_info.addWidget(self.etiquette_nom_magasin)

        self.etiquette_nom_gerant = QLabel("Gérant : N/A")
        self.etiquette_nom_gerant.setStyleSheet("font-size: 14px; color: #333;")
        self.etiquette_nom_gerant.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_pile_info.addWidget(self.etiquette_nom_gerant)

        self.etiquette_adresse_magasin = QLabel("Adresse : N/A")
        self.etiquette_adresse_magasin.setStyleSheet("font-size: 14px; color: #333;")
        self.etiquette_adresse_magasin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_pile_info.addWidget(self.etiquette_adresse_magasin)

        self.layout_barre_superieure.addStretch(1)
        self.layout_barre_superieure.addLayout(self.layout_pile_info)
        self.layout_barre_superieure.addStretch(1)
        
        self.barre_superieure_toolbar.addWidget(self.widget_barre_superieure)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.barre_superieure_toolbar)

        # --- Contenu principal : Visionneuse d'images ---
        self.visionneuse_image = VueImage()
        self.setCentralWidget(self.visionneuse_image)

        # --- Docks pour la liste de produits et la liste de courses ---
        self.dock_produits_disponibles = QDockWidget('Produits Disponibles')
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_produits_disponibles)
        self.dock_produits_disponibles.setMaximumWidth(400)

        self.liste_widget_produits_disponibles = QListWidget()
        self.liste_widget_produits_disponibles.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        # Widget et contrôles de la liste de courses
        conteneur_liste_courses = QWidget()
        layout_liste_courses = QVBoxLayout(conteneur_liste_courses)
        
        etiquette_disponible = QLabel("Produits disponibles dans le magasin :")
        etiquette_disponible.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        layout_liste_courses.addWidget(etiquette_disponible)
        layout_liste_courses.addWidget(self.liste_widget_produits_disponibles)

        self.bouton_ajouter_liste = QPushButton("Ajouter à la liste de courses")
        layout_liste_courses.addWidget(self.bouton_ajouter_liste)

        etiquette_liste_courses = QLabel("Ma liste de courses :")
        etiquette_liste_courses.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px; margin-bottom: 5px;")
        layout_liste_courses.addWidget(etiquette_liste_courses)

        self.liste_widget_courses = QListWidget()
        self.liste_widget_courses.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout_liste_courses.addWidget(self.liste_widget_courses)

        layout_boutons_liste_courses = QHBoxLayout()
        self.bouton_retirer_liste = QPushButton("Retirer")
        layout_boutons_liste_courses.addWidget(self.bouton_retirer_liste)

        self.bouton_effacer_liste = QPushButton("Tout effacer")
        layout_boutons_liste_courses.addWidget(self.bouton_effacer_liste)

        self.bouton_enregistrer_liste = QPushButton("Enregistrer la liste")
        layout_boutons_liste_courses.addWidget(self.bouton_enregistrer_liste)
        
        layout_liste_courses.addLayout(layout_boutons_liste_courses)

        self.dock_produits_disponibles.setWidget(conteneur_liste_courses)

        # --- Barre d'état ---
        self.barre_etat = QStatusBar()
        self.setStatusBar(self.barre_etat)
        self.barre_etat.showMessage("Veuillez ouvrir un plan de magasin...", 2000)

        # --- Barre de menu ---
        barre_menu = self.menuBar()

        menu_fichier = barre_menu.addMenu('&Fichier')
        menu_affichage = barre_menu.addMenu('&Affichage')

        self.action_ouvrir_plan = menu_fichier.addAction('Ouvrir un plan de magasin')
        menu_fichier.addSeparator()
        self.action_quitter = menu_fichier.addAction('Quitter')

        self.action_basculer_dock = menu_affichage.addAction('Afficher/Masquer le panneau des produits')
        self.action_basculer_dock.setCheckable(True)
        self.action_basculer_dock.setChecked(True) # Le dock est visible par défaut

    def appliquerStyles(self):
        """Applique un style cohérent aux différents widgets."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f8f8;
            }
            QDockWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QDockWidget::title {
                background: #e0e0e0;
                padding: 5px;
                border-bottom: 1px solid #ccc;
            }
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 3px;
            }
            QListWidget::item:selected {
                background-color: #a0c0e0;
                color: black;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                margin: 5px 0;
            }
            QPushButton:hover {
                background-color: #005999;
            }
            QLabel {
                color: #333;
            }
        """)

    # --- Méthodes pour mettre à jour l'interface utilisateur en fonction des données du modèle ---
    def mettreAJourInfosMagasin(self, infos_magasin: dict):
        """Met à jour les QLabels dans la barre supérieure avec les données du magasin chargées."""
        self.etiquette_nom_magasin.setText(f"Magasin : {infos_magasin.get('nom_magasin', 'Aucun plan chargé')}")
        self.etiquette_nom_gerant.setText(f"Gérant : {infos_magasin.get('auteur', 'N/A')}")
        self.etiquette_adresse_magasin.setText(f"Adresse : {infos_magasin.get('adresse_magasin', 'N/A')}")

    def afficherCarte(self, pixmap: QPixmap):
        """Affiche le pixmap donné sur la visionneuse d'images."""
        self.visionneuse_image.definirPixmapCarte(pixmap)

    def afficherProduitsDisponibles(self, produits_par_categorie: dict):
        """Remplit le widget de liste des produits disponibles."""
        self.liste_widget_produits_disponibles.clear()
        if not produits_par_categorie:
            item = QListWidgetItem("Aucun produit disponible dans ce magasin.")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled) # Le rendre non sélectionnable
            self.liste_widget_produits_disponibles.addItem(item)
            return

        for categorie, produits in produits_par_categorie.items():
            item_categorie = QListWidgetItem(f"--- {categorie} ---")
            item_categorie.setFlags(item_categorie.flags() & ~Qt.ItemFlag.ItemIsSelectable) # Rendre la catégorie non sélectionnable
            item_categorie.setForeground(QColor("blue"))
            self.liste_widget_produits_disponibles.addItem(item_categorie)

            for produit in produits:
                item = QListWidgetItem(produit)
                self.liste_widget_produits_disponibles.addItem(item)

    def afficherPositionsProduitsSurCarte(self, positions_produits: dict):
        """Affiche les étiquettes de produits sur la carte en fonction de leurs positions."""
        self.visionneuse_image.effacerToutesEtiquettesProduit()
        for nom_produit, donnees_pos in positions_produits.items():
            x = donnees_pos.get('x')
            y = donnees_pos.get('y')
            if x is not None and y is not None:
                self.visionneuse_image.placerEtiquetteProduit(nom_produit, x, y)

    def mettreAJourAffichageListeCourses(self, liste_courses: list[str]):
        """Met à jour le widget de la liste de courses avec la liste actuelle."""
        self.liste_widget_courses.clear()
        for produit in liste_courses:
            self.liste_widget_courses.addItem(QListWidgetItem(produit))

    def afficherMessageStatut(self, message: str, delai: int = 2000):
        """Affiche un message dans la barre d'état."""
        self.barre_etat.showMessage(message, delai)

    def afficherMessageInfo(self, titre: str, message: str):
        """Affiche une boîte de message d'information."""
        QMessageBox.information(self, titre, message)

    def afficherMessageAvertissement(self, titre: str, message: str):
        """Affiche une boîte de message d'avertissement."""
        QMessageBox.warning(self, titre, message)

    def afficherMessageCritique(self, titre: str, message: str):
        """Affiche une boîte de message d'erreur critique."""
        QMessageBox.critical(self, titre, message)

    def poserQuestionOuiNon(self, titre: str, message: str) -> bool:
        """Pose une question oui/non et renvoie True si Oui est sélectionné."""
        reponse = QMessageBox.question(self, titre, message,
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
        return reponse == QMessageBox.StandardButton.Yes

    def obtenirNomFichierOuvrir(self, legende: str, filtre: str) -> str:
        """Ouvre une boîte de dialogue de fichier pour ouvrir un fichier et renvoie le chemin du fichier sélectionné."""
        chemin_fichier, _ = QFileDialog.getOpenFileName(self, legende, "", filtre)
        return chemin_fichier

    def obtenirNomFichierEnregistrer(self, legende: str, nom_par_defaut: str, filtre: str) -> str:
        """Ouvre une boîte de dialogue de fichier pour enregistrer un fichier et renvoie le chemin du fichier sélectionné."""
        chemin_fichier, _ = QFileDialog.getSaveFileName(self, legende, nom_par_defaut, filtre)
        return chemin_fichier

    def basculerVisibiliteDockListeProduits(self, visible: bool):
        """Contrôle la visibilité du dock de la liste de produits."""
        self.dock_produits_disponibles.setVisible(visible)
        self.action_basculer_dock.setChecked(visible)