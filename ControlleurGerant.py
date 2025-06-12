import Magasin
import ihm_gerant

class ControllerGerant():
    def __init__(self, page_questionnaire):
        self.magasin = None
        page_questionnaire.questionnaire_valide.connect(self.creer_magasin)

    def creer_magasin(self, data):
        import datetime
        date_str = data.get("date_creation")
        date = datetime.date.fromisoformat(date_str) if date_str else None

        self.magasin = Magasin(
            nomProjet=data.get("nom_projet"),
            auteurProjet=data.get("auteur"),
            date=date,
            nomMagasin=data.get("nom_magasin"),
            adresse=data.get("adresse_magasin"),
            listeProduitsDispo=[],
            longueur=62,
            largeur=47
        )
        print("Magasin créé :", self.magasin.getNomMagasin())