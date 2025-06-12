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

        self.zoom = 0
        self.estVide = True
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.elementPixmap = QGraphicsPixmapItem()
        self.scene.addItem(self.elementPixmap)

        self.elementsTexteProduit = {} # Pour stocker les QGraphicsTextItem pour chaque produit

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    def definirPixmapCarte(self, pixmap: QPixmap):
        """Définit le pixmap d'arrière-plan pour la scène."""
        self.zoom = 0
        self.elementPixmap.setPixmap(pixmap)
        self.scene.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.estVide = False
        self.elementPixmap.setZValue(0) # S'assurer que le pixmap est en bas de la valeur Z

    def placerEtiquetteProduit(self, nomProduit: str, x: float, y: float):
        """
        Place une étiquette de produit sur la carte aux coordonnées de scène données.
        Supprime l'étiquette existante pour le même produit si présente.
        """
        # Supprimer l'étiquette existante pour ce produit si elle est déjà sur la carte
        if nomProduit in self.elementsTexteProduit:
            self.scene.removeItem(self.elementsTexteProduit[nomProduit])
            del self.elementsTexteProduit[nomProduit]

        # Créer un nouvel élément de texte pour le produit
        elementTexte = self.scene.addText(nomProduit)
        elementTexte.setDefaultTextColor(QColor("red")) # Les produits seront rouges pour les clients
        elementTexte.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        # Positionner l'élément de texte de manière à ce que son centre soit à (x, y)
        elementTexte.setPos(x - elementTexte.boundingRect().width() / 2,
                             y - elementTexte.boundingRect().height() / 2)

        elementTexte.setZValue(1) # S'assurer que les étiquettes de produit sont au-dessus de la carte
        self.elementsTexteProduit[nomProduit] = elementTexte

    def effacerToutesEtiquettesProduit(self):
        """Supprime toutes les étiquettes de produit actuellement affichées sur la carte."""
        for item in list(self.elementsTexteProduit.values()):
            self.scene.removeItem(item)
        self.elementsTexteProduit.clear()

    def wheelEvent(self, event: QWheelEvent):
        """Gère les événements de la molette de la souris pour le zoom."""
        if self.estVide:
            return

        facteurZoomAvant = 1.25
        facteurZoomArriere = 1 / facteurZoomAvant

        if event.angleDelta().y() > 0:
            facteurZoom = facteurZoomAvant
            self.zoom += 1
        else:
            facteurZoom = facteurZoomArriere
            self.zoom -= 1

        # Empêcher le zoom excessif
        if self.zoom < -10:
            self.zoom = -10
            return
        if self.zoom > 30:
            self.zoom = 30
            return

        self.scale(facteurZoom, facteurZoom)


# --- Fenêtre principale de l'application ---
class FenetreAppliVue(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application Client de Magasin")
        geometrieEcran = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(geometrieEcran)

        self.configurerUI()
        self.appliquerStyles()
        self.showMaximized()

    def configurerUI(self):
        # --- Barre supérieure pour les informations du magasin ---
        self.barreSuperieureToolbar = QToolBar("Informations du Magasin")
        self.barreSuperieureToolbar.setMovable(False)
        self.barreSuperieureToolbar.toggleViewAction().setVisible(False)
        
        self.widgetBarreSuperieure = QWidget()
        self.layoutBarreSuperieure = QHBoxLayout(self.widgetBarreSuperieure)
        self.widgetBarreSuperieure.setFixedHeight(90)
        self.widgetBarreSuperieure.setStyleSheet("background-color: #f0f0f0;")

        self.layoutPileInfo = QVBoxLayout()
        self.layoutPileInfo.setContentsMargins(0, 0, 0, 0)
        self.layoutPileInfo.setSpacing(2)

        self.etiquetteNomMagasin = QLabel("Magasin : Aucun plan chargé")
        self.etiquetteNomMagasin.setStyleSheet("font-size: 20px; font-weight: bold; color: #005999;")
        self.etiquetteNomMagasin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layoutPileInfo.addWidget(self.etiquetteNomMagasin)

        self.etiquetteNomGerant = QLabel("Gérant : N/A")
        self.etiquetteNomGerant.setStyleSheet("font-size: 14px; color: #333;")
        self.etiquetteNomGerant.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layoutPileInfo.addWidget(self.etiquetteNomGerant)

        self.etiquetteAdresseMagasin = QLabel("Adresse : N/A")
        self.etiquetteAdresseMagasin.setStyleSheet("font-size: 14px; color: #333;")
        self.etiquetteAdresseMagasin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layoutPileInfo.addWidget(self.etiquetteAdresseMagasin)

        self.layoutBarreSuperieure.addStretch(1)
        self.layoutBarreSuperieure.addLayout(self.layoutPileInfo)
        self.layoutBarreSuperieure.addStretch(1)
        
        self.barreSuperieureToolbar.addWidget(self.widgetBarreSuperieure)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.barreSuperieureToolbar)

        # --- Contenu principal : Visionneuse d'images ---
        self.visionneuseImage = VueImage()
        self.setCentralWidget(self.visionneuseImage)

        # --- Docks pour la liste de produits et la liste de courses ---
        self.dockProduitsDisponibles = QDockWidget('Produits Disponibles')
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockProduitsDisponibles)
        self.dockProduitsDisponibles.setMaximumWidth(400)

        self.listeWidgetProduitsDisponibles = QListWidget()
        self.listeWidgetProduitsDisponibles.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        # Widget et contrôles de la liste de courses
        conteneurListeCourses = QWidget()
        layoutListeCourses = QVBoxLayout(conteneurListeCourses)
        
        etiquette_disponible = QLabel("Produits disponibles dans le magasin :")
        etiquette_disponible.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        layoutListeCourses.addWidget(etiquette_disponible)
        layoutListeCourses.addWidget(self.listeWidgetProduitsDisponibles)

        self.boutonAjouterListe = QPushButton("Ajouter à la liste de courses")
        layoutListeCourses.addWidget(self.boutonAjouterListe)

        etiquetteListeCourses = QLabel("Ma liste de courses :")
        etiquetteListeCourses.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px; margin-bottom: 5px;")
        layoutListeCourses.addWidget(etiquetteListeCourses)

        self.listeWidgetCourses = QListWidget()
        self.listeWidgetCourses.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layoutListeCourses.addWidget(self.listeWidgetCourses)

        layoutBoutonsListeCourses = QHBoxLayout()
        self.boutonRetirerListe = QPushButton("Retirer")
        layoutBoutonsListeCourses.addWidget(self.boutonRetirerListe)

        self.boutonEffacerListe = QPushButton("Tout effacer")
        layoutBoutonsListeCourses.addWidget(self.boutonEffacerListe)

        self.boutonEnregistrerListe = QPushButton("Enregistrer la liste")
        layoutBoutonsListeCourses.addWidget(self.boutonEnregistrerListe)
        
        layoutListeCourses.addLayout(layoutBoutonsListeCourses)

        self.dockProduitsDisponibles.setWidget(conteneurListeCourses)

        # --- Barre d'état ---
        self.barreEtat = QStatusBar()
        self.setStatusBar(self.barreEtat)
        self.barreEtat.showMessage("Veuillez ouvrir un plan de magasin...", 2000)

        # --- Barre de menu ---
        barreMenu = self.menuBar()

        menuFichier = barreMenu.addMenu('&Fichier')
        menuAffichage = barreMenu.addMenu('&Affichage')

        self.actionOuvrirPlan = menuFichier.addAction('Ouvrir un plan de magasin')
        menuFichier.addSeparator()
        self.actionQuitter = menuFichier.addAction('Quitter')

        self.actionBasculerDock = menuAffichage.addAction('Afficher/Masquer le panneau des produits')
        self.actionBasculerDock.setCheckable(True)
        self.actionBasculerDock.setChecked(True) # Le dock est visible par défaut

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
    def mettreAJourInfosMagasin(self, infosMagasin: dict):
        """Met à jour les QLabels dans la barre supérieure avec les données du magasin chargées."""
        self.etiquetteNomMagasin.setText(f"Magasin : {infosMagasin.get('nom_magasin', 'Aucun plan chargé')}")
        self.etiquetteNomGerant.setText(f"Gérant : {infosMagasin.get('auteur', 'N/A')}")
        self.etiquetteAdresseMagasin.setText(f"Adresse : {infosMagasin.get('adresse_magasin', 'N/A')}")

    def afficherCarte(self, pixmap: QPixmap):
        """Affiche le pixmap donné sur la visionneuse d'images."""
        self.visionneuseImage.definirPixmapCarte(pixmap)

    def afficherProduitsDisponibles(self, produitsParCategorie: dict):
        """Remplit le widget de liste des produits disponibles."""
        self.listeWidgetProduitsDisponibles.clear()
        if not produitsParCategorie:
            item = QListWidgetItem("Aucun produit disponible dans ce magasin.")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled) # Le rendre non sélectionnable
            self.listeWidgetProduitsDisponibles.addItem(item)
            return

        for categorie, produits in produitsParCategorie.items():
            itemCategorie = QListWidgetItem(f"--- {categorie} ---")
            itemCategorie.setFlags(itemCategorie.flags() & ~Qt.ItemFlag.ItemIsSelectable) # Rendre la catégorie non sélectionnable
            itemCategorie.setForeground(QColor("blue"))
            self.listeWidgetProduitsDisponibles.addItem(itemCategorie)

            for produit in produits:
                item = QListWidgetItem(produit)
                self.listeWidgetProduitsDisponibles.addItem(item)

    def afficherPositionsProduitsSurCarte(self, positionProduits: dict):
        """Affiche les étiquettes de produits sur la carte en fonction de leurs positions."""
        self.visionneuseImage.effacerToutesEtiquettesProduit()
        for nomProduit, donneesPos in positionProduits.items():
            x = donneesPos.get('x')
            y = donneesPos.get('y')
            if x is not None and y is not None:
                self.visionneuseImage.placerEtiquetteProduit(nomProduit, x, y)

    def mettreAJourAffichageListeCourses(self, listeCourses: list[str]):
        """Met à jour le widget de la liste de courses avec la liste actuelle."""
        self.listeWidgetCourses.clear()
        for produit in listeCourses:
            self.listeWidgetCourses.addItem(QListWidgetItem(produit))

    def afficherMessageStatut(self, message: str, delai: int = 2000):
        """Affiche un message dans la barre d'état."""
        self.barreEtat.showMessage(message, delai)

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
        cheminFichier, _ = QFileDialog.getOpenFileName(self, legende, "", filtre)
        return cheminFichier

    def obtenirNomFichierEnregistrer(self, legende: str, nomParDefaut: str, filtre: str) -> str:
        """Ouvre une boîte de dialogue de fichier pour enregistrer un fichier et renvoie le chemin du fichier sélectionné."""
        cheminFichier, _ = QFileDialog.getSaveFileName(self, legende, nomParDefaut, filtre)
        return cheminFichier

    def basculerVisibiliteDockListeProduits(self, visible: bool):
        """Contrôle la visibilité du dock de la liste de produits."""
        self.dockProduitsDisponibles.setVisible(visible)
        self.actionBasculerDock.setChecked(visible)