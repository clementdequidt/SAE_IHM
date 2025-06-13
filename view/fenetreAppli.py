from .imageWidget import ImageWidget
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import json
import os
import sys

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
        self.imageViewer = ImageWidget(self.__chemin)
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
            
class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item is None:
            return
        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setText(item.text())
        drag.setMimeData(mimeData)
        drag.exec(Qt.DropAction.MoveAction)