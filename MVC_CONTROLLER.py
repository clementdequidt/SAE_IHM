# MVC_CONTROLEUR.py
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap
from MVC_MODEL import ModeleMagasin # Correctement importé
from MVC_VIEW import FenetreAppliVue # Correctement importé

class ControleurMagasin:
    def __init__(self, modele: ModeleMagasin, vue: FenetreAppliVue):
        self._modele = modele
        self._vue = vue
        self.connecterSignaux()
        self.mettreAJourVueDepuisModele() # Mise à jour initiale de la vue

    def connecterSignaux(self):
        """Connecte les signaux de l'interface utilisateur aux slots du contrôleur."""
        self._vue.action_ouvrir_plan.triggered.connect(self.gererOuvrirPlanMagasin)
        self._vue.action_quitter.triggered.connect(QApplication.instance().quit)
        self._vue.action_basculer_dock.triggered.connect(self.gererBasculerDockListeProduits)
        self._vue.bouton_ajouter_liste.clicked.connect(self.gererAjouterSelectionAListeCourses)
        self._vue.bouton_retirer_liste.clicked.connect(self.gererRetirerSelectionDeListeCourses)
        self._vue.bouton_effacer_liste.clicked.connect(self.gererEffacerListeCourses)
        self._vue.bouton_enregistrer_liste.clicked.connect(self.gererEnregistrerListeCourses)

    def mettreAJourVueDepuisModele(self):
        """Met à jour toutes les parties de la vue en fonction de l'état actuel du modèle."""
        self._vue.mettreAJourInfosMagasin(self._modele.infos_magasin) # Corrected
        
        if self._modele.chemin_image_carte: # Corrected
            self._vue.afficherCarte(QPixmap(self._modele.chemin_image_carte)) # Corrected
        else:
            # Effacer la carte si aucune image n'est définie (par exemple, après le chargement initial ou une erreur)
            self._vue.visionneuse_image.definirPixmapCarte(QPixmap()) 

        self._vue.afficherProduitsDisponibles(self._modele.produits_disponibles) # Corrected
        self._vue.afficherPositionsProduitsSurCarte(self._modele.positions_produits) # Corrected
        self._vue.mettreAJourAffichageListeCourses(self._modele.liste_courses) # Corrected

    # --- Gestionnaires des actions de l'interface utilisateur (rôle du contrôleur) ---
    def gererOuvrirPlanMagasin(self):
        """Gère l'action d'ouvrir un plan de magasin."""
        self._vue.afficherMessageStatut('Ouverture du plan du magasin...', 2000)
        chemin_fichier = self._vue.obtenirNomFichierOuvrir(
            "Ouvrir un plan de magasin sauvegardé",
            "Fichiers de magasin (*.json)"
        )
        if chemin_fichier:
            succes, message = self._modele.charger_plan_magasin(chemin_fichier) # Corrected
            if succes:
                self.mettreAJourVueDepuisModele()
                self._vue.afficherMessageStatut(message, 3000)
            else:
                self._vue.afficherMessageCritique("Erreur de fichier", message)
                self._vue.afficherMessageStatut('Échec du chargement du plan du magasin.', 2000)
        else:
            self._vue.afficherMessageStatut('Ouverture du plan du magasin annulée.', 2000)

    def gererBasculerDockListeProduits(self):
        """Gère le basculement de la visibilité du dock de la liste de produits."""
        est_visible = self._vue.dock_produits_disponibles.isVisible()
        self._vue.basculerVisibiliteDockListeProduits(not est_visible)
        if not est_visible:
            self._vue.afficherMessageStatut("Panneau des produits affiché.", 2000)
        else:
            self._vue.afficherMessageStatut("Panneau des produits masqué.", 2000)

    def gererAjouterSelectionAListeCourses(self):
        """Ajoute les éléments sélectionnés parmi les produits disponibles à la liste de courses."""
        selected_items = self._vue.liste_widget_produits_disponibles.selectedItems()
        if not selected_items:
            self._vue.afficherMessageInfo("Sélection vide", "Veuillez sélectionner au moins un produit à ajouter.")
            return

        nombre_ajoutes = 0
        for item in selected_items:
            nom_produit = item.text()
            if not nom_produit.startswith("---"): # Éviter d'ajouter les en-têtes de catégorie
                self._modele.ajouterProduitAListeCourses(nom_produit) # Corrected
                nombre_ajoutes += 1
        
        self._vue.mettreAJourAffichageListeCourses(self._modele.liste_courses) # Corrected
        if nombre_ajoutes > 0:
            self._vue.afficherMessageStatut(f"{nombre_ajoutes} produits ajoutés à la liste de courses.", 2000)
        else:
            self._vue.afficherMessageStatut("Aucun produit ajouté à la liste de courses.", 2000)


    def gererRetirerSelectionDeListeCourses(self):
        """Supprime les éléments sélectionnés de la liste de courses."""
        elements_selectionnes = self._vue.liste_widget_courses.selectedItems()
        if not elements_selectionnes:
            self._vue.afficherMessageInfo("Sélection vide", "Veuillez sélectionner au moins un produit à retirer.")
            return
        
        produits_a_retirer = [item.text() for item in elements_selectionnes]
        self._modele.retirerProduitsDeListeCourses(produits_a_retirer) # Corrected
        self._vue.mettreAJourAffichageListeCourses(self._modele.liste_courses) # Corrected
        self._vue.afficherMessageStatut(f"{len(elements_selectionnes)} produits retirés de la liste de courses.", 2000)

    def gererEffacerListeCourses(self):
        """Efface tous les éléments de la liste de courses."""
        if not self._modele.liste_courses: # Corrected
            self._vue.afficherMessageInfo("Liste vide", "La liste de courses est déjà vide.")
            return

        if self._vue.poserQuestionOuiNon('Effacer la liste', "Êtes-vous sûr de vouloir effacer toute la liste de courses ?"):
            self._modele.effacerListeCourses() # Corrected
            self._vue.mettreAJourAffichageListeCourses(self._modele.liste_courses) # Corrected
            self._vue.afficherMessageStatut("Liste de courses effacée.", 2000)

    def gererEnregistrerListeCourses(self):
        """Enregistre la liste de courses actuelle dans un fichier texte."""
        if not self._modele.liste_courses: # Corrected
            self._vue.afficherMessageInfo("Liste vide", "La liste de courses est vide et ne peut pas être enregistrée.")
            return

        chemin_fichier = self._vue.obtenirNomFichierEnregistrer(
            "Enregistrer la liste de courses",
            "ma_liste_courses.txt",
            "Fichiers texte (*.txt);;Tous les fichiers (*)"
        )
        if chemin_fichier:
            succes, message = self._modele.enregistrerListeCourses(chemin_fichier) # Corrected
            if succes:
                self._vue.afficherMessageStatut(message, 3000)
                self._vue.afficherMessageInfo("Enregistrement réussi", f"Votre liste de courses a été enregistrée à :\n{chemin_fichier}")
            else:
                self._vue.afficherMessageCritique("Erreur d'enregistrement", message)