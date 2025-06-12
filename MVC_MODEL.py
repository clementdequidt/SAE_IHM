# MVC_MODELE.py
import json
import os
import Magasin # Assuming Magasin is a relevant module, keeping its name as is unless specified
from collections import defaultdict

class ModeleMagasin:
    def __init__(self):
        self._infos_magasin = {
            "nom_magasin": "Aucun plan chargé",
            "auteur": "N/A",
            "adresse_magasin": "N/A"
        }
        self._chemin_image_carte = None
        self._produits_disponibles = defaultdict(list) # Catégorie -> [noms des produits]
        self._positions_produits = {} # Nom du produit -> {'x': float, 'y': float}
        self._liste_courses = [] # Liste des noms de produits

    # --- Propriétés pour accéder aux données ---
    @property
    def infos_magasin(self):
        return self._infos_magasin

    @property
    def chemin_image_carte(self):
        return self._chemin_image_carte

    @property
    def produits_disponibles(self):
        return self._produits_disponibles

    @property
    def positions_produits(self):
        return self._positions_produits

    @property
    def liste_courses(self):
        return self._liste_courses[:] # Retourne une copie pour éviter les modifications externes

    # --- Chargement / Enregistrement des données ---
    def charger_plan_magasin(self, chemin_fichier: str):
        """
        Charge les données du plan du magasin à partir d'un fichier JSON.
        Retourne (succès: bool, message: str)
        """
        if not chemin_fichier:
            return False, "Ouverture annulée."

        try:
            with open(chemin_fichier, 'r', encoding='utf-8') as f:
                donnees_projet = json.load(f)

            # Mettre à jour les informations du magasin
            self._infos_magasin = donnees_projet.get("questionnaire_info", {})
            
            # Mettre à jour le chemin de l'image de la carte
            chemin_image = donnees_projet.get("chemin_image_plan")
            if not os.path.exists(chemin_image):
                return False, f"Image de la carte '{chemin_image}' introuvable. Veuillez vérifier le chemin ou charger un autre plan."
            self._chemin_image_carte = chemin_image

            # Mettre à jour les produits disponibles
            self._produits_disponibles = defaultdict(list, donnees_projet.get("produits_selectionnes", {}))

            # Mettre à jour les positions des produits
            self._positions_produits = donnees_projet.get("positions_produits_finales", {})
            
            # Effacer la liste de courses lorsqu'un nouveau plan de magasin est chargé
            self._liste_courses.clear()

            return True, f"Plan du magasin chargé avec succès depuis {chemin_fichier}"

        except json.JSONDecodeError:
            return False, "Le fichier sélectionné n'est pas un fichier JSON valide."
        except Exception as e:
            return False, f"Échec du chargement du plan du magasin : {e}"

    def ajouterProduitAListeCourses(self, nom_produit: str):
        """Ajoute un produit à la liste de courses."""
        self._liste_courses.append(nom_produit)

    def retirerProduitsDeListeCourses(self, noms_produits: list[str]):
        """Supprime les produits spécifiés de la liste de courses.
        Si plusieurs instances du même produit existent, une instance par nom fourni est supprimée.
        """
        for nom_produit in noms_produits:
            if nom_produit in self._liste_courses:
                self._liste_courses.remove(nom_produit)

    def effacerListeCourses(self):
        """Efface tous les produits de la liste de courses."""
        self._liste_courses.clear()

    def enregistrerListeCourses(self, chemin_fichier: str):
        """
        Enregistre la liste de courses actuelle dans un fichier texte.
        Retourne (succès: bool, message: str)
        """
        if not self._liste_courses:
            return False, "La liste de courses est vide et ne peut pas être enregistrée."

        try:
            with open(chemin_fichier, 'w', encoding='utf-8') as f:
                for produit in self._liste_courses:
                    f.write(produit + '\n')
            return True, f"Liste de courses enregistrée dans {chemin_fichier}"
        except Exception as e:
            return False, f"Échec de l'enregistrement de la liste de courses : {e}"