#Fichier crée par Bastien COUSIN, Pierre DELDALLE, Clément DEQUIDT, Sébastien GROUÉ
# MVC_MODELE.py
import json
import os
from collections import defaultdict
import Magasin

class ModeleMagasin:
    def __init__(self):
        self.infosMagasin = {
            "nom_magasin": "Aucun plan chargé",
            "auteur": "N/A",
            "adresse_magasin": "N/A"
        }
        self.cheminImageCarte = None
        self.produitsDisponibles = defaultdict(list) # Catégorie -> [noms des produits]
        self.positionsProduits = {} # Nom du produit -> {'x': float, 'y': float}
        self.listeCourses = [] # Liste des noms de produits

    # --- Propriétés pour accéder aux données ---
    
    def infosMagasin(self):
        """
        Renvoie les informations du magasin
        """
        return self.infosMagasin

    def cheminImageCarte(self):
        """
        Renvoie le chemin sur la carte
        """
        return self.cheminImageCarte

    def produitsDisponibles(self):
        """
        Renvoie les position des produits disponibles
        """
        return self.produitsDisponibles
    
    def positionsProduits(self):
        """
        Renvoie la position des produits
        """
        return self.positionsProduits

    def listeCourses(self):
        """
        Renvoie la liste de courses
        """
        return self.listeCourses[:] # Retourne une copie pour éviter les modifications externes

    # --- Chargement / Enregistrement des données ---
    def chargerPlanMagasin(self, cheminFichier: str):
        """
        Charge les données du plan du magasin à partir d'un fichier JSON.
        Retourne (succès: bool, message: str)
        """
        if not cheminFichier:
            return False, "Ouverture annulée."

        try:
            with open(cheminFichier, 'r', encoding='utf-8') as f:
                donneesProjet = json.load(f)

            # Mettre à jour les informations du magasin
            self.infosMagasin = donneesProjet.get("questionnaire_info", {})
            
            # Mettre à jour le chemin de l'image de la carte
            cheminImage = donneesProjet.get("chemin_image_plan")
            if not os.path.exists(cheminImage):
                return False, f"Image de la carte '{cheminImage}' introuvable. Veuillez vérifier le chemin ou charger un autre plan."
            self.cheminImageCarte = cheminImage

            # Mettre à jour les produits disponibles
            self.produitsDisponibles = defaultdict(list, donneesProjet.get("produits_selectionnes", {}))

            # Mettre à jour les positions des produits
            self.positionsProduits = donneesProjet.get("positions_produits_finales", {})
            
            # Effacer la liste de courses lorsqu'un nouveau plan de magasin est chargé
            self.listeCourses.clear()

            return True, f"Plan du magasin chargé avec succès depuis {cheminFichier}"

        except json.JSONDecodeError:
            return False, "Le fichier sélectionné n'est pas un fichier JSON valide."
        except Exception as e:
            return False, f"Échec du chargement du plan du magasin : {e}"

    def ajouterProduitAListeCourses(self, nomProduit: str):
        """Ajoute un produit à la liste de courses."""
        self.listeCourses.append(nomProduit)

    def retirerProduitsDeListeCourses(self, nomsProduits: list[str]):
        """Supprime les produits spécifiés de la liste de courses.
        Si plusieurs instances du même produit existent, une instance par nom fourni est supprimée.
        """
        for nomProduit in nomsProduits:
            if nomProduit in self.listeCourses:
                self.listeCourses.remove(nomProduit)

    def effacerListeCourses(self):
        """Efface tous les produits de la liste de courses."""
        self.listeCourses.clear()

    def enregistrerListeCourses(self, cheminFichier: str):
        """
        Enregistre la liste de courses actuelle dans un fichier texte.
        Retourne (succès: bool, message: str)
        """
        if not self.listeCourses:
            return False, "La liste de courses est vide et ne peut pas être enregistrée."

        try:
            with open(cheminFichier, 'w', encoding='utf-8') as f:
                for produit in self.listeCourses:
                    f.write(produit + '\n')
            return True, f"Liste de courses enregistrée dans {cheminFichier}"
        except Exception as e:
            return False, f"Échec de l'enregistrement de la liste de courses : {e}"
    
    def calculerCheminListeCourses(self, cheminFichier: str):
        """
        Calcule le chemin optimal pour la liste de courses en utilisant l'algorithme de Magasin.
        Retourne une liste contenant le chemin des produits dans l'ordre optimal,
        ou (False, message) en cas d'erreur.
        """
        if not self.listeCourses:
            return False, "La liste de courses est vide. Veuillez ajouter des produits avant de calculer le chemin."
        try:
            magasin = Magasin.Magasin(
                nomProjet = self.infosMagasin.get("nom_projet", "Aucun projet"),
                auteurProjet = self.infosMagasin.get("auteur", "N/A"),
                date = self.infosMagasin.get("date_creation", "N/A"),
                nomMagasin = self.infosMagasin.get("nom_magasin", "Aucun magasin"),
                adresse = self.infosMagasin.get("adresse_magasin", "N/A"),
                listeProduitsDispo = self.produitsDisponibles
            )
            chemin = magasin.calculerChemin(self.listeCourses, self.positionsProduits)
            return chemin
        except Exception as e:
            return False, f"Échec du calcul du chemin pour la liste de courses : {e}"