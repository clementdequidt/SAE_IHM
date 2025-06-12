import sys
import platform
import json
import os
import ControlleurGerant

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QMessageBox, QTextEdit, QDockWidget, QStackedWidget, QStatusBar, QFileDialog, QDateEdit, QScrollArea, QCheckBox, QListWidget, QListWidgetItem,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsRectItem
)
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QIcon, QDrag, QMouseEvent, QWheelEvent, QPainter, QBrush, QColor, QFont, QPen, QDragMoveEvent, QDragLeaveEvent
from PyQt6.QtCore import Qt, QDate, QPointF, QRectF, pyqtSignal, QMimeData, QCoreApplication

#Fonction pour détecter le système d'exploitation du client
def detecterThemeSysteme():
    if platform.system() == "Windows":
        try:
            import winreg #importation de winreg pour lire, écrire et modifier le registre de Windows
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            keyPath = r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize'
            key = winreg.OpenKey(registry, keyPath)
            appsUseLightTheme, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
            return "clair" if appsUseLightTheme == 1 else "sombre"
        except Exception:
            return "clair"
    return "clair"
#Si le système d'exploitation est différents de windows la couleur est de base blanche

#Page de questionnaire pour crée son magasin
class PageQuestionnaire(QWidget):
    questionnaireValide = pyqtSignal(dict)
    
    def __init__(self, switchCallback):
        super().__init__()
        self.switchCallback = switchCallback

        formLayout = QVBoxLayout() #layout vertical pour structurer le questionnaire
        formLayout.setContentsMargins(40, 40, 40, 40)
        formLayout.setSpacing(15) #Espacement de 15 entre chaque layout

        title = QLabel("Création d'un nouveau magasin") #Label pour préciser ce que l'on fais
        title.setStyleSheet("font-size: 24px; font-weight: bold;") #Police utilisé, caractère, taille et mise en gras
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        formLayout.addWidget(title)

        self.projetInput = self.ajouterLabelInput("Nom du projet :", "Saisissez le nom du projet", formLayout) #Ajout d'un label pour saisir le nom du projet
        self.auteurInput = self.ajouterLabelInput("Votre nom  :", "Saisissez votre nom", formLayout) #Ajout d'un label pour saisir notre nom 
        self.dateInput = self.ajouterDateInput("Date de création :", formLayout) #Ajout d'un label pour saisir la date de création

        self.nomMagasinInput = self.ajouterLabelInput("Nom du magasin :", "Nom du magasin", formLayout)  #Ajout d'un label pour saisir le nom du magasin
        self.adresseMagasinInput = self.ajouterLabelInput("Adresse du magasin :", "Adresse complète", formLayout) #Ajout d'un label pour saisir l'adresse du magasin

        btnValider = QPushButton("Valider") #Un bouton pour valider
        btnValider.clicked.connect(self.verifierEtPasser)#Appel d'une fonction, si tout les champs
        #sont complé alors on peut passer sinon on ne peut pas valider
        formLayout.addWidget(btnValider)

        outerLayout = QVBoxLayout() #Ajout d'un layout vertical
        outerLayout.addStretch()
        outerLayout.addLayout(formLayout)
        outerLayout.addStretch()
        self.setLayout(outerLayout)

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

    def ajouterLabelInput(self, labelText, placeholder, layout):
        layout.addWidget(QLabel(labelText))
        line = QLineEdit()
        line.setPlaceholderText(placeholder)
        layout.addWidget(line)
        return line

    def ajouterDateInput(self, labelText, layout):
        layout.addWidget(QLabel(labelText))
        dateEdit = QDateEdit()
        dateEdit.setCalendarPopup(True)
        dateEdit.setDate(QDate.currentDate())
        layout.addWidget(dateEdit)
        return dateEdit

    #Si tout les champs ne sont pas vérifier et rempli alors on renvoie un warning pour dire que les champs sont nécessaires
    def verifierEtPasser(self):
        if not all([
            self.projetInput.text().strip(),
            self.auteurInput.text().strip(),
            self.nomMagasinInput.text().strip(),
            self.adresseMagasinInput.text().strip()
        ]):
            QMessageBox.warning(self, "Champs requis", "Veuillez remplir tous les champs.")
            return
        self.questionnaireValide.emit(self.getQuestionnaireData())
        self.switchCallback()


    def getQuestionnaireData(self):
        return {
            "nom_projet": self.projetInput.text().strip(),
            "auteur": self.auteurInput.text().strip(),
            "date_creation": self.dateInput.date().toString(Qt.DateFormat.ISODate),
            "nom_magasin": self.nomMagasinInput.text().strip(),
            "adresse_magasin": self.adresseMagasinInput.text().strip()
        }

#Choisir les produits disponibles dans le magasin
class ChoisirProduits(QWidget):
    selectionValidee = pyqtSignal(dict)

    def __init__(self, fichierProduits='liste_produits.json'): #Appelle de la liste de produits (la même que celle donner par le prof)
        super().__init__()
        self.setWindowTitle("Choisir les produits disponibles")
        self.setGeometry(100, 100, 600, 500)

        self.fichierProduits = fichierProduits
        self.produitsParCategorie = {}
        self.categories = [] #Liste pour les catégories d'aliments
        self.pageCourante = 0
        self.categoriesParPage = 3 # Un nombre de 3 catégorie par page de l'application
        self.listesCategorie = {} # Contient les QListWidget actuellement affichés
        self.selectionsGlobales = {}  #Dictionnaire pour stocker toutes les sélections (produit -> est_sélectionné)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        titre = QLabel("Sélectionnez les produits disponibles :")
        titre.setObjectName("titrePrincipal")
        self.layout.addWidget(titre)

        self.scroll = QScrollArea() #Pouvoir sélectionner les produits en scrollant
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)

        self.container = QWidget()
        self.scroll.setWidget(self.container)
        self.containerLayout = QHBoxLayout()
        self.container.setLayout(self.containerLayout)

        navLayout = QHBoxLayout()
        self.btnPrecedent = QPushButton("Page Précédente") #Boutton précédent pour aller dans la page d'avant
        self.btnPrecedent.clicked.connect(self.pagePrecedente)
        navLayout.addWidget(self.btnPrecedent)
        self.btnSuivant = QPushButton("Page Suivante") #Boutton suivant pour aller dans la page d'après
        self.btnSuivant.clicked.connect(self.pageSuivante)
        navLayout.addWidget(self.btnSuivant)
        self.layout.addLayout(navLayout)

        self.btnValider = QPushButton("Valider la sélection") #Boutton pour valider la sélection de produits
        self.btnValider.clicked.connect(self.validerSelection)
        self.layout.addWidget(self.btnValider)

        self.chargerProduits()
        
    #Fonction pour charger les produits
    def chargerProduits(self):
        try:
            currentDir = os.path.dirname(os.path.abspath(__file__))
            filePath = os.path.join(currentDir, self.fichierProduits)

            with open(filePath, 'r', encoding='utf-8') as f: #On ouvre en mode lecture le fichier
                self.produitsParCategorie = json.load(f) #On charge forcément un .json
        except FileNotFoundError:
            QMessageBox.critical(self, "Erreur", f"Le fichier '{self.fichierProduits}' n'a pas été trouvé. Veuillez vous assurer qu'il est dans le même répertoire que l'application.")
            self.produitsParCategorie = {}
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Erreur", f"Erreur de lecture du fichier '{self.fichierProduits}'. Assurez-vous qu'il s'agit d'un fichier JSON valide.")
            self.produitsParCategorie = {}
        except Exception as e: #Si on ne trouve ou on n'a pas le fichier alors on renvoie une erreur
            QMessageBox.critical(self, "Erreur", f"Impossible de charger la liste des produits:\n{e}")
            self.produitsParCategorie = {}
            
        #Initialiser selectionsGlobales avec tous les produits non sélectionnés au départ
        for categorie, produits in self.produitsParCategorie.items():
            for produit in produits:
                self.selectionsGlobales[produit] = False

        self.categories = list(self.produitsParCategorie.keys())
        self.pageCourante = 0
        self.afficherPage()

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

    #Fonction qui sauvegarde les produits sélectionner actuellement
    def sauvegarderSelectionsCourantes(self):
        """Sauvegarde l'état des QListWidget actuellement affichés dans selectionsGlobales."""
        for categorie, listeWidget in self.listesCategorie.items():
            for i in range(listeWidget.count()):
                item = listeWidget.item(i)
                if item.flags() & Qt.ItemFlag.ItemIsSelectable:
                    self.selectionsGlobales[item.text()] = item.isSelected()

    def afficherPage(self):
        #Sauvegarder les sélections AVANT de vider les listes
        self.sauvegarderSelectionsCourantes()

        # Nettoyage des widgets précédents
        for i in reversed(range(self.containerLayout.count())):
            layoutOrWidget = self.containerLayout.itemAt(i)
            if layoutOrWidget is not None:
                widget = layoutOrWidget.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    childLayout = layoutOrWidget.layout()
                    if childLayout is not None:
                        self.clearLayout(childLayout)
                        self.containerLayout.removeItem(childLayout)
                    else:
                        self.containerLayout.removeItem(layoutOrWidget)

        self.listesCategorie = {}  # Réinitialise pour les nouvelles listes

        start = self.pageCourante * self.categoriesParPage
        end = start + self.categoriesParPage
        categoriesaAfficher = self.categories[start:end]

        for categorie in categoriesaAfficher:
            produits = self.produitsParCategorie[categorie]
            layoutCategorie = QVBoxLayout()

            label = QLabel(categorie)
            label.setObjectName("categorieLabel")
            layoutCategorie.addWidget(label)

            listeWidget = QListWidget()
            listeWidget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
            for produit in produits:
                item = QListWidgetItem(produit)
                #Restaurer la sélection de l'item si elle était sauvegardée
                if self.selectionsGlobales.get(produit, False): # Par défaut à False si pas trouvé
                    item.setSelected(True)
                listeWidget.addItem(item)
            layoutCategorie.addWidget(listeWidget)

            self.containerLayout.addLayout(layoutCategorie)
            self.listesCategorie[categorie] = listeWidget

        self.btnPrecedent.setEnabled(self.pageCourante > 0)
        self.btnSuivant.setEnabled(end < len(self.categories))

    def clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                childLayout = item.layout()
                if childLayout is not None:
                    self.clearLayout(childLayout)

    def pagePrecedente(self):
        #Sauvegarder les sélections avant de retourner dans la page précédente 
        self.sauvegarderSelectionsCourantes()
        if self.pageCourante > 0:
            self.pageCourante -= 1
            self.afficherPage()

    def pageSuivante(self):
        #Sauvegarder les sélections avant d'aller dans la prochaine page
        self.sauvegarderSelectionsCourantes()
        if (self.pageCourante + 1) * self.categoriesParPage < len(self.categories):
            self.pageCourante += 1
            self.afficherPage()

    def validerSelection(self):
        #S'assurer que les sélections de la page actuelle sont sauvegardées avant validation
        self.sauvegarderSelectionsCourantes()

        selectionFinale = {}
        totalSelectionnes = 0
        # Parcourir les sélectionsGlobales pour construire la selectionFinale
        for produit, selected in self.selectionsGlobales.items():
            if selected:
                # Retrouver la catégorie du produit pour le classer
                for categorie, produitsListe in self.produitsParCategorie.items():
                    if produit in produitsListe:
                        if categorie not in selectionFinale:
                            selectionFinale[categorie] = []
                        selectionFinale[categorie].append(produit)
                        totalSelectionnes += 1
                        break # Produit trouvé, passer au suivant
        
        #Si le nombre de produit est inférieur a 20 alors message d'erreur pour nous dire qu'il faut un minima de 20 produits
        if totalSelectionnes < 20:
            QMessageBox.warning(
                self,
                "Sélection insuffisante",
                f"Veuillez choisir au moins 20 produits (actuellement : {totalSelectionnes})."
            )
            return

        self.selectionValidee.emit(selectionFinale)

class Image(QGraphicsView):
    produitPlaceSignal = pyqtSignal(str, QPointF)

    #Taille d'une case
    CELL_SIZE = 51

    def __init__(self, chemin: str):
        super().__init__()

        self.zoom = 0 # Le zoom
        self.empty = True
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        #Pour afficher l'image
        self.pixmapItem = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmapItem)
        
        #stocker les cellules de la case
        self.gridCells = []
        self.productTextItems = {}
        self.productPositionsHistory = [] 
        self.historyIndex = -1 

        #Configure le point de zoom 
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        #Cache les barres de défilement
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        #Accepte le drag and drop
        self.setAcceptDrops(True)

        #Pour changer l'image grâce au chemin du fichier
        pixmap = QPixmap(chemin)
        if pixmap.isNull():
            label = QLabel(f"Image non trouvée : {chemin}") #Si le chemin de l'image n'est pas trouvé
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scene.addWidget(label)
        else:
            self.setPixmap(pixmap) #Sinon on affiche l'image

    def setPixmap(self, pixmap: QPixmap):
        #Met le zoom a zero
        self.zoom = 0
        self.pixmapItem.setPixmap(pixmap)
        
        #Définit la taille de la scène à celle de l’image
        self.scene.setSceneRect(QRectF(pixmap.rect()))
        
        #Pour mettre l'image dans la fenêtre
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.empty = False
        self.drawGridOverlay()
        
        #Remettre a vide l'historique
        self.ProductPositionsHistory = []
        self.historyIndex = -1

    def drawGridOverlay(self):
        
        # Supprime les cellules de la grille
        for cell in self.gridCells:
            self.scene.removeItem(cell)
        self.gridCells.clear()

        #Pour reprendre la taille de l'image
        imageWidth = self.pixmapItem.pixmap().width()
        imageHeight = self.pixmapItem.pixmap().height()

        gridColorBorder = QColor(255, 0, 0, 100)
        gridPen = QPen(gridColorBorder)
        gridPen.setWidth(2)

        # Crée une grille rectangulaire par-dessus l’image
        for y in range(0, imageHeight, self.CELL_SIZE):
            for x in range(0, imageWidth, self.CELL_SIZE):
                rectItem = QGraphicsRectItem(x, y, self.CELL_SIZE, self.CELL_SIZE)
                rectItem.setPen(gridPen)
                self.scene.addItem(rectItem)
                self.gridCells.append(rectItem)
                rectItem.setZValue(1) #Pour mettre la grille par dessus notre image

        self.pixmapItem.setZValue(0)

    def placerProduit(self, productName: str, x: float, y: float, recordHistory=True):
        if productName in self.productTextItems:
            self.scene.removeItem(self.productTextItems[productName])
            del self.productTextItems[productName]

        textItem = QGraphicsTextItem(productName)
        textItem.setDefaultTextColor(QColor("red"))
        textItem.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        textItem.setPos(x - textItem.boundingRect().width() / 2,
                         y - textItem.boundingRect().height() / 2)

        textItem.setZValue(2)
        self.scene.addItem(textItem)
        self.productTextItems[productName] = textItem

        if recordHistory:
            del self.productPositionsHistory[self.historyIndex + 1:]
            self.productPositionsHistory.append((productName, QPointF(x, y)))
            self.historyIndex += 1

    def retirerProduit(self, productName: str):
        if productName in self.productTextItems:
            self.scene.removeItem(self.productTextItems[productName])
            del self.productTextItems[productName]

    def enleverDerniereAction(self):
        if self.historyIndex >= 0:
            lastAction = self.productPositionsHistory[self.historyIndex]
            productNameToRemove = lastAction[0]
            self.retirerProduit(productNameToRemove)
            self.historyIndex -= 1
            self.produits()
            return True
        return False

    def rajouterDerniereAction(self):
        if self.historyIndex + 1 < len(self.productPositionsHistory):
            self.historyIndex += 1
            actionToRedo = self.productPositionsHistory[self.historyIndex]
            self.placerProduit(actionToRedo[0], actionToRedo[1].x(), actionToRedo[1].y(), recordHistory=False)
            return True
        return False

    def produits(self):
        for productItem in list(self.productTextItems.values()):
            self.scene.removeItem(productItem)
        self.productTextItems.clear()

        for i in range(self.historyIndex + 1):
            productName, position = self.productPositionsHistory[i]
            self.placerProduit(productName, position.x(), position.y(), recordHistory=False)


    def wheelEvent(self, event: QWheelEvent):
        if self.empty:
            return

        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
            self.zoom += 1
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= 1

        if self.zoom < -10:
            self.zoom = -10
            return
        if self.zoom > 30:
            self.zoom = 30
            return

        self.scale(zoomFactor, zoomFactor)

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

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasText():
            productName = event.mimeData().text()
            scenePos = self.mapToScene(event.position().toPoint())

            gridX = (int(scenePos.x()) // self.CELL_SIZE) * self.CELL_SIZE
            gridY = (int(scenePos.y()) // self.CELL_SIZE) * self.CELL_SIZE

            centerX = gridX + self.CELL_SIZE / 2
            centerY = gridY + self.CELL_SIZE / 2

            self.placerProduit(productName, centerX, centerY, recordHistory=True)

            event.acceptProposedAction()
            self.produitPlaceSignal.emit(productName, QPointF(centerX, centerY))
        else:
            event.ignore()

# Nouvelle classe personnalisée pour le QListWidget
class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True) # Active le glisser-déposer depuis cette liste
        self.setDragDropMode(QListWidget.DragDropMode.DragOnly) # Permet seulement de glisser, pas de déposer sur la liste
        self.setDefaultDropAction(Qt.DropAction.MoveAction) # Action par défaut est le déplacement

    def startDrag(self, supportedActions):
        # Récupère l'élément qui a été cliqué pour commencer le glisser
        item = self.currentItem()
        if item is None:
            return # Aucun élément à glisser

        # S'assurer que ce n'est pas un titre de catégorie ou un élément non glissable
        if not (item.flags() & Qt.ItemFlag.ItemIsDragEnabled):
            return

        mimeData = QMimeData()
        mimeData.setText(item.text()) # C'est la ligne clé : s'assurer que le texte est dans le QMimeData

        drag = QDrag(self)
        drag.setMimeData(mimeData)

        # Exécute l'opération de glisser
        drag.exec(supportedActions)

class FenetreAppli(QMainWindow):
    def __init__(self, chemin: str = None, produitsSelectionnes: dict = None, questionnaireData: dict = None):
        super().__init__()
        self.__chemin = chemin
        self.produitsSelectionnes = produitsSelectionnes if produitsSelectionnes is not None else {}
        self.positionsProduits = {} 
        self.questionnaireData = questionnaireData if questionnaireData is not None else {}

        self.setWindowTitle("Gestionnaire de Magasin (Gérant)")
        screenHeometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screenHeometry)
       
        self.topBarWidget = QWidget()
        self.topBarLayout = QHBoxLayout() 
        self.topBarWidget.setLayout(self.topBarLayout)
        self.topBarWidget.setFixedHeight(90) 
        
        self.infoStackLayout = QVBoxLayout()
        self.infoStackLayout.setContentsMargins(0, 0, 0, 0) 
        self.infoStackLayout.setSpacing(2) 

        self.storeNameLabel = QLabel("Magasin : N/A")
        self.storeNameLabel.setObjectName("storeNameLabel")
        self.storeNameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.infoStackLayout.addWidget(self.storeNameLabel)
        self.storeNameLabel.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.gerantNameLabel = QLabel("Gérant : N/A")
        self.gerantNameLabel.setObjectName("gerantNameLabel")
        self.gerantNameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.infoStackLayout.addWidget(self.gerantNameLabel)
        self.gerantNameLabel.setStyleSheet("font-size: 16px;")

        self.storeAddressLabel = QLabel("Adresse : N/A")
        self.storeAddressLabel.setObjectName("storeAddressLabel")
        self.storeAddressLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.infoStackLayout.addWidget(self.storeAddressLabel)
        self.storeAddressLabel.setStyleSheet("font-size: 16px;")

        self.topBarLayout.addStretch(1) 
        self.topBarLayout.addLayout(self.infoStackLayout) 
        self.topBarLayout.addStretch(1) 

        self.mainContentWidget = QWidget()
        self.mainLayout = QVBoxLayout(self.mainContentWidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        self.mainLayout.addWidget(self.topBarWidget)
        self.imageViewer = Image(self.__chemin)
        self.mainLayout.addWidget(self.imageViewer) 
        self.setCentralWidget(self.mainContentWidget) 

        self.imageViewer.produitPlaceSignal.connect(self.enregistrerPositionProduit)

        self.dock = QDockWidget('Produits à placer')
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        self.dock.setMaximumWidth(400)

        self.listeProduitsDock = DraggableListWidget()
        self.dock.setWidget(self.listeProduitsDock)

        self.afficherProduitsDansDock()

        self.barreEtat = QStatusBar()
        self.setStatusBar(self.barreEtat)
        self.barreEtat.showMessage("Application démarrée. Choisissez un plan et placez les produits.", 2000)

        menuBar = self.menuBar()
        menuFichier = menuBar.addMenu('&Fichier')
        menuEdition = menuBar.addMenu('&Edition')
        menuAffichage = menuBar.addMenu('&Affichage')

        menuFichier.addAction('Nouveau plan', self.nouveau)
        menuFichier.addAction('Ouvrir un plan', self.ouvrir)
        menuFichier.addAction('Enregistrer les positions temporaires', self.enregistrerPositions) 
        menuFichier.addAction('Enregistrer le plan final', self.enregistrerPlanFinal) 
        menuFichier.addSeparator()
        menuFichier.addAction('Quitter', QCoreApplication.instance().quit) 

        self.actionUndo = menuEdition.addAction('Annuler', self.annulerAction)
        self.actionRedo = menuEdition.addAction('Rétablir', self.refaireAction)
        self.actionUndo.setShortcut('Ctrl+Z')
        self.actionRedo.setShortcut('Ctrl+Y')
        self.mettreAJourDerniereAction() 

        self.actionToggleDock = menuAffichage.addAction('Afficher/Masquer la liste des produits', self.basculerListeProduits)
        self.actionToggleDock.setCheckable(True)
        self.actionToggleDock.setChecked(True) 

        self.showMaximized()

        self.mettreAJourMagasin() 

    def mettreAJourMagasin(self):
        """Updates all the QLabels in the top bar with data from questionnaire_data."""
        nomMagasin = self.questionnaireData.get("nom_magasin", "N/A")
        auteur = self.questionnaireData.get("auteur", "N/A")
        adresseMagasin = self.questionnaireData.get("adresse_magasin", "N/A")

        self.storeNameLabel.setText(f"Magasin : {nomMagasin}")
        self.gerantNameLabel.setText(f"Gérant : {auteur}")
        self.storeAddressLabel.setText(f"Adresse : {adresseMagasin}")

    def mettreAJourDerniereAction(self):
        self.actionUndo.setEnabled(self.imageViewer.historyIndex >= 0)
        self.actionRedo.setEnabled(self.imageViewer.historyIndex + 1 < len(self.imageViewer.productPositionsHistory))

    def afficherProduitsDansDock(self):
        self.listeProduitsDock.clear()
        if not self.produitsSelectionnes:
            item = QListWidgetItem("Aucun produit sélectionné dans le questionnaire.")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled & ~Qt.ItemFlag.ItemIsDragEnabled & ~Qt.ItemFlag.ItemIsSelectable)
            self.listeProduitsDock.addItem(item)
            return

        for categorie, produits in self.produitsSelectionnes.items():
            categoryItem = QListWidgetItem(f"--- {categorie} ---")
            categoryItem.setFlags(categoryItem.flags() & ~Qt.ItemFlag.ItemIsDragEnabled & ~Qt.ItemFlag.ItemIsSelectable)
            categoryItem.setForeground(QBrush(QColor("blue")))
            self.listeProduitsDock.addItem(categoryItem)

            for produit in produits:
                item = QListWidgetItem(produit)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsSelectable)
                self.listeProduitsDock.addItem(item)

    def enregistrerPositionProduit(self, productName: str, position: QPointF):
        self.positionsProduits[productName] = {'x': position.x(), 'y': position.y()}
        self.barreEtat.showMessage(f"Produit '{productName}' placé à ({position.x():.0f}, {position.y():.0f})", 3000)
        self.mettreAJourDerniereAction()

    #Fonction pour vérifier si l'utilisateur peut retourner ou non en arrière
    def annulerAction(self):
        if self.imageViewer.enleverDerniereAction():
            self.positionsProduits.clear()
            
             #Recherche dans l'historique l'action a annuler
            for productName, pos in self.imageViewer.productPositionsHistory[:self.imageViewer.historyIndex + 1]:
                self.positionsProduits[productName] = {'x': pos.x(), 'y': pos.y()}
            self.barreEtat.showMessage("Action annulée.", 2000) #Message affiché si l'action a été supprimée
        else:
            self.barreEtat.showMessage("Aucune action à annuler.", 2000) #Pas d'action à annuler
        self.mettreAJourDerniereAction()
    #Fonction pour rétablir l'action annulée juste avant
    def refaireAction(self):
        if self.imageViewer.rajouterDerniereAction():
            #Recherche dans l'historique l'action à rétablir
            productName, pos = self.imageViewer.productPositionsHistory[self.imageViewer.historyIndex]
            self.positionsProduits[productName] = {'x': pos.x(), 'y': pos.y()}
            self.barreEtat.showMessage("Action rétablie.", 2000) #Message affiché si l'action a été rétablie
        else:
            self.barreEtat.showMessage("Aucune action à rétablir.", 2000) #Pas d'action à rétablir
        self.mettreAJourDerniereAction()

    #Fonction pour afficher ou masquer la liste des produits sur l'interface
    def basculerListeProduits(self):
        
        #Action pour masquer la liste des produits
        if self.dock.isVisible():
            self.dock.hide()
            self.actionToggleDock.setChecked(False)
            self.barreEtat.showMessage("Liste des produits masquée.", 2000)
        else:
            #Action pour afficher la liste des produits
            self.dock.show()
            self.actionToggleDock.setChecked(True)
            self.barreEtat.showMessage("Liste des produits affichée.", 2000)

    #Fonction qui enregistre les positions temporaires des produits dans un fichier JSON
    def enregistrerPositions(self):
        if not self.positionsProduits: #si il n'y a pas de produit placé sur le plan
            QMessageBox.information(self, "Enregistrer les positions temporaires", "Aucun produit n'a été placé pour être enregistré temporairement.")
            return #Quitte la fonction comme il y a rien a enregistrer
        #Enregistre la ou le fichier JSON sera enregistré

        filePath, _ = QFileDialog.getSaveFileName(self, "Enregistrer les positions temporaires des produits",
                                                 "positions_temp.json",
                                                 "JSON Files (*.json)")
        if filePath: #vérifie que l'utilisateur a choisi un fichier
            try:
                #Ecrit dans le fichier JSON les positions des produits
                with open(filePath, 'w', encoding='utf-8') as f:
                    serializablePositions = {
                        name: {'x': pos['x'], 'y': pos['y']}
                        for name, pos in self.positionsProduits.items()
                    }
                    json.dump(serializablePositions, f, indent=4, ensure_ascii=False)
                self.barreEtat.showMessage(f"Positions temporaires enregistrées dans {filePath}", 3000)
                #Exception pour capturer toutes les erreurs possibles pendant l'enregistrement
            except Exception as e:
                #Message d'erreur
                QMessageBox.critical(self, "Erreur d'enregistrement", f"Impossible d'enregistrer les positions temporaires:\n{e}")

    def enregistrerPlanFinal(self):
        #Sauvegarde les données complètes du projet : questionnaire, produits sélectionnés, le chemin de l'image du plan et les positions du produit final.

        #Vérifie si le plan a été chargé correctement
        if not self.__chemin:
            QMessageBox.warning(self, "Enregistrer le plan final", "Aucun plan de magasin n'est chargé.")
            return

        #Vérifie si des produits ont été sélectionnés
        if not self.produitsSelectionnes:
            QMessageBox.warning(self, "Enregistrer le plan final", "Aucun produit n'a été sélectionné pour le magasin.")
            return

        #Vérifie si des produits ont été placés sur le plan
        if not self.positionsProduits:
            QMessageBox.warning(self, "Enregistrer le plan final", "Aucun produit n'a été placé sur le plan.")
            return

        #Création du dictionnaire qui contient les données
        projectData = {
            "questionnaire_info": self.questionnaireData,
            "chemin_image_plan": self.__chemin,
            "produits_selectionnes": self.produitsSelectionnes,
            "positions_produits_finales": {
                name: {'x': pos['x'], 'y': pos['y']}
                for name, pos in self.positionsProduits.items()
            }
        }

        #Choisir ou enregistrer le fihcier JSON
        filePath, _ = QFileDialog.getSaveFileName(self, "Enregistrer le plan final du magasin",
                                                 "mon_magasin_final.json",
                                                 "Fichiers Magasin (*.json)")
        if filePath:
            try:
                #Ecrit dans le fichier JSON les données du projet
                with open(filePath, 'w', encoding='utf-8') as f:
                    json.dump(projectData, f, indent=4, ensure_ascii=False)
                self.barreEtat.showMessage(f"Plan final enregistré dans {filePath}", 5000)
                QMessageBox.information(self, "Enregistrement réussi", f"Le plan final du magasin a été enregistré dans :\n{filePath}")
                
                #Exception pour capturer toutes les erreurs possibles pendant l'enregistrement
            except Exception as e:
                
                #Message d'erreur
                QMessageBox.critical(self, "Erreur d'enregistrement", f"Impossible d'enregistrer le plan final:\n{e}")


    def nouveau(self):
        self.barreEtat.showMessage('Création d\'un nouveau plan...', 2000)
        boite = QFileDialog()
        chemin, validation = boite.getOpenFileName(self, "Sélectionner un nouveau plan de magasin",
                                                 directory = os.path.join(sys.path[0]),
                                                 filter="Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if validation:
            self.__chemin = chemin
            self.imageViewer.setPixmap(QPixmap(self.__chemin))
            self.positionsProduits.clear()
            self.imageViewer.productPositionsHistory = [] 
            self.imageViewer.historyIndex = -1
            self.mettreAJourDerniereAction()
            self.barreEtat.showMessage('Nouveau plan chargé. Vous pouvez placer des produits.', 2000)
        else:
            self.barreEtat.showMessage('Création de nouveau plan annulée.', 2000)

    def ouvrir(self):
        self.barreEtat.showMessage('Ouvrir un plan existant....', 2000)
        filePath, _ = QFileDialog.getOpenFileName(self, "Ouvrir un plan de magasin enregistré",
                                                 "", 
                                                 "Fichiers Magasin (*.json)")
        if filePath:
            try:
                with open(filePath, 'r', encoding='utf-8') as f:
                    projectData = json.load(f)

                cheminImage = projectData.get("chemin_image_plan")
                if not os.path.exists(cheminImage):
                    QMessageBox.warning(self, "Erreur", f"L'image du plan '{cheminImage}' n'a pas été trouvée. Veuillez la replacer ou choisir un nouveau plan.")
                    return

                self.__chemin = cheminImage
                self.imageViewer.setPixmap(QPixmap(self.__chemin))

                self.questionnaireData = projectData.get("questionnaire_info", {})
                self.mettreAJourMagasin() 

                self.produitsSelectionnes = projectData.get("produits_selectionnes", {})
                self.afficherProduitsDansDock()

                self.positionsProduits.clear()
                self.imageViewer.productPositionsHistory = [] 
                self.imageViewer.historyIndex = -1
                
                for itemGraphic in list(self.imageViewer.productTextItems.values()):
                    self.imageViewer.scene.removeItem(itemGraphic)
                self.imageViewer.productTextItems.clear()

                loadedPositions = projectData.get("positions_produits_finales", {})
                for productName, posData in loadedPositions.items():
                    x = posData.get('x')
                    y = posData.get('y')
                    if x is not None and y is not None:
                        self.imageViewer.placerProduit(productName, x, y, recordHistory=True)
                        self.positionsProduits[productName] = {'x': x, 'y': y}

                self.barreEtat.showMessage(f"Plan chargé: {filePath}", 3000)
                self.mettreAJourDerniereAction()


            except json.JSONDecodeError:
                QMessageBox.critical(self, "Erreur d'ouverture", "Le fichier sélectionné n'est pas un fichier JSON valide.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'ouverture", f"Impossible d'ouvrir le plan:\n{e}")
        else:
            self.barreEtat.showMessage('Ouverture de plan annulée.', 2000)


# Gestionnaire de navigation entre pages
class AppMultiPages(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.pageQuestionnaire = PageQuestionnaire(self.allerAChoisirProduits)
        self.addWidget(self.pageQuestionnaire)  # index 0

        self.choisirProduits = ChoisirProduits()
        self.choisirProduits.selectionValidee.connect(self.allerAFenetreAppli)
        self.addWidget(self.choisirProduits) # index 1

        self.fenetreAppli = None

        self.setCurrentIndex(0)

    def allerAChoisirProduits(self):
        self.setCurrentIndex(1)
        self.choisirProduits.chargerProduits()

    def allerAFenetreAppli(self, produitsSelectionnes: dict):
        cheminImage = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Quadrillage_Final.jpg')
        questionnaireData = self.pageQuestionnaire.getQuestionnaireData() 

        if self.fenetreAppli is None:
            self.fenetreAppli = FenetreAppli(
                chemin=cheminImage,
                produitsSelectionnes=produitsSelectionnes,
                questionnaireData=questionnaireData 
            )
            self.addWidget(self.fenetreAppli)  # index 2
        else:
            self.fenetreAppli.produitsSelectionnes = produitsSelectionnes
            self.fenetreAppli.questionnaireData = questionnaireData 
            self.fenetreAppli.afficherProduitsDansDock()
            self.fenetreAppli.positionsProduits.clear()
            self.fenetreAppli.imageViewer.productPositionsHistory = [] 
            self.fenetreAppli.imageViewer.historyIndex = -1
            for item in list(self.fenetreAppli.imageViewer.productTextItems.values()):
                self.fenetreAppli.imageViewer.Scene.removeItem(item)
            self.fenetreAppli.imageViewer.productTextItems.clear()
            self.fenetreppli.imageViewer.drawGridOverlay() 
            self.fenetreAppli.mettreAJourMagasin() 
            self.fenetreAppli.mettreAJourDerniereAction()


        self.setCurrentIndex(2)

# Mise en place d'un mot de passe pour accéder à l'application gérant
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

# Fonction qui permet de vérifier si le mot de passe entré est correct ou non
    def verifierMdp(self):
        if self.champMdp.text() == self.motDePasseAttendu:
            self.callbackConnexion()
            self.close() #si mot de passe correct, on ferme la fenêtre de connexion et on lance la "vraie" application
        else:
            QMessageBox.critical(self, "Erreur", "Mot de passe incorrect.") #mot de passe incorrect, message d'erreur + faut recommencer
            
#Lancement de l'application
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