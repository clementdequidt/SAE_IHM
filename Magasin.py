from Plan import Plan
import datetime as dt

class Magasin():
    def init(self, nomProjet: str, auteurProjet: str, date: dt, nomMagasin: str, adresse: str, longueur: int = 62, largeur: int = 47):
        self.__nomProjet = nomProjet
        self.__auteurProjet = auteurProjet
        self.__date = dt.datetime
        self.__nomMagasin = nomMagasin
        self.__adresse = adresse
        self.__plan = Plan(longueur, largeur)

    def getNomProjet(self):
        return self.__nomProjet
    
    def getAuteurProjet(self):
        return self.__auteurProjet
    
    def getDate(self):
        return self.__date
    
    def getNomMagasin(self):
        return self.__nomMagasin
    
    def getAdresse(self):
        return self.__adresse
    
    def getPlan(self):
        return self.__plan
    
    def setNomProjet(self, nomProjet: str):
        self.__nomProjet = nomProjet
        
    def setAuteurProjet(self, auteurProjet: str):
        self.__auteurProjet = auteurProjet
        
    def setDate(self, date: dt):
        self.__date = date
        
    def setNomMagasin(self, nomMagasin: str):
        self.__nomMagasin = nomMagasin
        
    def setAdresse(self, adresse: str):
        self.__adresse = adresse
        
    def setPlan(self, plan: Plan):
        self.__plan = plan

    def remplirMagasin(self):
        print("Remplissage du magasin...")
        self.__plan.remplirPlan()

    def afficher_etat(self):
        print("Etat du magasin")
        for y in range(self.plan.getLargeur()):
            ligne = []
            for x in range(self.plan.getLongueur()):
                case = self.plan.getCase((x, y))
                if case.isDepart():
                    ligne.append("D")
                elif case.isRayon():
                    ligne.append("R")
                elif case.isObstacle():
                    ligne.append("O")
                else:
                    ligne.append(".")
            print(" ".join(ligne))

    def get_case(self, coord):
        return self.plan.getCase(coord)

    def set_items_accessible(self, coord):
        self.plan.setItemsAccessible(coord)