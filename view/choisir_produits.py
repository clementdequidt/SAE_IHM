import os
import json
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

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