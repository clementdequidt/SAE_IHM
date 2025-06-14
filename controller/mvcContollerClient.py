#Fichier crée par Bastien COUSIN, Pierre DELDALLE, Clément DEQUIDT, Sébastien GROUÉ
# MVC_CONTROLEUR.py
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap
from model.mvcModeleClient import ModeleMagasin # Correctement importé
from view.mvcVueClient import FenetreAppliVue # Correctement importé

class ControleurMagasin:
    def __init__(self, modele: ModeleMagasin, vue: FenetreAppliVue):
        self.modele = modele
        self.vue = vue
        self.connecterSignaux()
        self.mettreAJourVueDepuisModele() # Mise à jour initiale de la vue

    def connecterSignaux(self):
        """Connecte les signaux de l'interface utilisateur aux slots du contrôleur."""
        self.vue.actionOuvrirPlan.triggered.connect(self.gererOuvrirPlanMagasin)
        self.vue.actionQuitter.triggered.connect(QApplication.instance().quit)
        self.vue.actionBasculerDock.triggered.connect(self.gererBasculerDockListeProduits)
        self.vue.boutonAjouterListe.clicked.connect(self.gererAjouterSelectionAListeCourses)
        self.vue.boutonRetirerListe.clicked.connect(self.gererRetirerSelectionDeListeCourses)
        self.vue.boutonEffacerListe.clicked.connect(self.gererEffacerListeCourses)
        self.vue.boutonEnregistrerListe.clicked.connect(self.gererEnregistrerListeCourses)
        self.vue.boutonCalculerChemin.clicked.connect(self.calculerChemin)

    def mettreAJourVueDepuisModele(self):
        """Met à jour toutes les parties de la vue en fonction de l'état actuel du modèle."""
        self.vue.mettreAJourInfosMagasin(self.modele.infosMagasin) # Corrected
        
        if self.modele.cheminImageCarte: # Corrected
            self.vue.afficherCarte(QPixmap(self.modele.cheminImageCarte)) # Corrected
        else:
            # Effacer la carte si aucune image n'est définie (par exemple, après le chargement initial ou une erreur)
            self.vue.visionneuseImage.definirPixmapCarte(QPixmap()) 

        self.vue.afficherProduitsDisponibles(self.modele.produitsDisponibles) # Corrected
        self.vue.afficherPositionsProduitsSurCarte(self.modele.positionsProduits) # Corrected
        self.vue.mettreAJourAffichageListeCourses(self.modele.listeCourses) # Corrected

    # --- Gestionnaires des actions de l'interface utilisateur (rôle du contrôleur) ---
    def gererOuvrirPlanMagasin(self):
        """Gère l'action d'ouvrir un plan de magasin."""
        self.vue.afficherMessageStatut('Ouverture du plan du magasin...', 2000)
        cheminFichier = self.vue.obtenirNomFichierOuvrir(
            "Ouvrir un plan de magasin sauvegardé",
            "Fichiers de magasin (*.json)"
        )
        if cheminFichier:
            succes, message = self.modele.chargerPlanMagasin(cheminFichier) # Corrected
            if succes:
                self.mettreAJourVueDepuisModele()
                self.vue.afficherMessageStatut(message, 3000)
            else:
                self.vue.afficherMessageCritique("Erreur de fichier", message)
                self.vue.afficherMessageStatut('Échec du chargement du plan du magasin.', 2000)
        else:
            self.vue.afficherMessageStatut('Ouverture du plan du magasin annulée.', 2000)

    def gererBasculerDockListeProduits(self):
        """Gère le basculement de la visibilité du dock de la liste de produits."""
        estVisible = self.vue.dockProduitsDisponibles.isVisible()
        self.vue.basculerVisibiliteDockListeProduits(not estVisible)
        if not estVisible:
            self.vue.afficherMessageStatut("Panneau des produits affiché.", 2000)
        else:
            self.vue.afficherMessageStatut("Panneau des produits masqué.", 2000)

    def gererAjouterSelectionAListeCourses(self):
        """Ajoute les éléments sélectionnés parmi les produits disponibles à la liste de courses."""
        selectedItems = self.vue.listeWidgetProduitsDisponibles.selectedItems()
        if not selectedItems:
            self.vue.afficherMessageInfo("Sélection vide", "Veuillez sélectionner au moins un produit à ajouter.")
            return

        nombreAjoutes = 0
        for item in selectedItems:
            nomProduit = item.text()
            if not nomProduit.startswith("---"): # Éviter d'ajouter les en-têtes de catégorie
                self.modele.ajouterProduitAListeCourses(nomProduit) # Corrected
                nombreAjoutes += 1
        
        self.vue.mettreAJourAffichageListeCourses(self.modele.listeCourses) # Corrected
        if nombreAjoutes > 0:
            self.vue.afficherMessageStatut(f"{nombreAjoutes} produits ajoutés à la liste de courses.", 2000)
        else:
            self.vue.afficherMessageStatut("Aucun produit ajouté à la liste de courses.", 2000)


    def gererRetirerSelectionDeListeCourses(self):
        """Supprime les éléments sélectionnés de la liste de courses."""
        elementsSelectionnes = self.vue.listeWidgetCourses.selectedItems()
        if not elementsSelectionnes:
            self.vue.afficherMessageInfo("Sélection vide", "Veuillez sélectionner au moins un produit à retirer.")
            return
        
        produitsARetirer = [item.text() for item in elementsSelectionnes]
        self.modele.retirerProduitsDeListeCourses(produitsARetirer) # Corrected
        self.vue.mettreAJourAffichageListeCourses(self.modele.listeCourses) # Corrected
        self.vue.afficherMessageStatut(f"{len(elementsSelectionnes)} produits retirés de la liste de courses.", 2000)

    def gererEffacerListeCourses(self):
        """Efface tous les éléments de la liste de courses."""
        if not self.modele.listeCourses: # Corrected
            self.vue.afficherMessageInfo("Liste vide", "La liste de courses est déjà vide.")
            return

        if self.vue.poserQuestionOuiNon('Effacer la liste', "Êtes-vous sûr de vouloir effacer toute la liste de courses ?"):
            self.modele.effacerListeCourses() # Corrected
            self.vue.mettreAJourAffichageListeCourses(self.modele.listeCourses) # Corrected
            self.vue.afficherMessageStatut("Liste de courses effacée.", 2000)

    def gererEnregistrerListeCourses(self):
        """Enregistre la liste de courses actuelle dans un fichier texte."""
        if not self.modele.listeCourses: # Corrected
            self.vue.afficherMessageInfo("Liste vide", "La liste de courses est vide et ne peut pas être enregistrée.")
            return

        cheminFichier = self.vue.obtenirNomFichierEnregistrer(
            "Enregistrer la liste de courses",
            "ma_liste_courses.txt",
            "Fichiers texte (*.txt);;Tous les fichiers (*)"
        )
        if cheminFichier:
            succes, message = self.modele.enregistrerListeCourses(cheminFichier) # Corrected
            if succes:
                self.vue.afficherMessageStatut(message, 3000)
                self.vue.afficherMessageInfo("Enregistrement réussi", f"Votre liste de courses a été enregistrée à :\n{cheminFichier}")
            else:
                self.vue.afficherMessageCritique("Erreur d'enregistrement", message)
    
    def calculerChemin(self):
        chemin, positionsItems = ModeleMagasin.calculerCheminListeCourses(self)
        if isinstance(chemin, list) and isinstance(positionsItems, dict):
            self.vue.afficherCheminListeCourses(chemin, positionsItems)