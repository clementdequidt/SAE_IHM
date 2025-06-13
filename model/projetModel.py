import json

class Projet:
    def __init__(self):
        self.nomProjet = ""
        self.auteur = ""
        self.dateCreation = ""
        self.nomMagasin = ""
        self.adresseMagasin = ""
        self.cheminImage = ""
        self.produitsSelectionnes = {}
        self.positionsProduits = {}

    def chargerQuestionnaire(self, data: dict):
        self.nomProjet = data.get("nomProjet", "")
        self.auteur = data.get("auteur", "")
        self.dateCreation = data.get("dateCreation", "")
        self.nomMagasin = data.get("nomMagasin", "")
        self.adresseMagasin = data.get("adresse_magasin", "")

    def exporterQuestionnaire(self):
        return {
            "nom_projet": self.nomProjet,
            "auteur": self.auteur,
            "date_creation": self.dateCreation,
            "nom_magasin": self.nomMagasin,
            "adresse_magasin": self.adresseMagasin,
        }

    def sauvegarderProjet(self, fichierPath):
        data = {
            "questionnaire_info": self.exporterQuestionnaire(),
            "chemin_image_plan": self.cheminImage,
            "produits_selectionnes": self.produitsSelectionnes,
            "positions_produits_finales": self.positionsProduits
        }
        with open(fichierPath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def chargerProjet(self, fichierPath):
        with open(fichierPath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.chargerQuestionnaire(data.get("questionnaire_info", {}))
        self.cheminImage = data.get("chemin_image_plan", "")
        self.produitsSelectionnes = data.get("produits_selectionnes", {})
        self.positionsProduits = data.get("positions_produits_finales", {})