import json

class Projet:
    def __init__(self):
        self.nom_projet = ""
        self.auteur = ""
        self.date_creation = ""
        self.nom_magasin = ""
        self.adresse_magasin = ""
        self.chemin_image = ""
        self.produits_selectionnes = {}
        self.positions_produits = {}

    def charger_questionnaire(self, data: dict):
        self.nom_projet = data.get("nom_projet", "")
        self.auteur = data.get("auteur", "")
        self.date_creation = data.get("date_creation", "")
        self.nom_magasin = data.get("nom_magasin", "")
        self.adresse_magasin = data.get("adresse_magasin", "")

    def exporter_questionnaire(self):
        return {
            "nom_projet": self.nom_projet,
            "auteur": self.auteur,
            "date_creation": self.date_creation,
            "nom_magasin": self.nom_magasin,
            "adresse_magasin": self.adresse_magasin,
        }

    def sauvegarder_projet(self, fichier_path):
        data = {
            "questionnaire_info": self.exporter_questionnaire(),
            "chemin_image_plan": self.chemin_image,
            "produits_selectionnes": self.produits_selectionnes,
            "positions_produits_finales": self.positions_produits
        }
        with open(fichier_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def charger_projet(self, fichier_path):
        with open(fichier_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.charger_questionnaire(data.get("questionnaire_info", {}))
        self.chemin_image = data.get("chemin_image_plan", "")
        self.produits_selectionnes = data.get("produits_selectionnes", {})
        self.positions_produits = data.get("positions_produits_finales", {})