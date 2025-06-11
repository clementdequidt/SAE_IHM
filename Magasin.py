from Plan import Plan
import datetime as dt

class Magasin():
    """Classe représentant un magasin."""
    
    # OK
    def init(self, nomProjet: str, auteurProjet: str, date: dt, nomMagasin: str, adresse: str, listeProduitsDispo: list, longueur: int = 62, largeur: int = 47):
        """Constructeur qui initialise un objet Magasin et ses attributs.
        
        Args:
            nomProjet (str): Nom du projet.
            auteurProjet (str): Auteur du projet.
            date (dt): Date de création du projet.
            nomMagasin (str): Nom du magasin.
            adresse (str): Adresse du magasin.
            listeProduitsDispo (list): Liste des produits disponibles dans le magasin.
            longueur (int): Longueur du plan du magasin. Par défaut, 62.
            largeur (int): Largeur du plan du magasin. Par défaut, 47.
        
        Attributes:
            __plan (Plan): Plan du magasin, représentant la disposition des cases.
        """
        self.__nomProjet = nomProjet
        self.__auteurProjet = auteurProjet
        self.__date = date
        self.__nomMagasin = nomMagasin
        self.__adresse = adresse
        self.__listeProduitsDispo = listeProduitsDispo
        self.__plan = Plan(longueur, largeur)

    # OK
    def getNomProjet(self):
        """Retourne le nom du projet.
        
        Returns:
            str: Nom du projet.
        """
        return self.__nomProjet
    
    # OK
    def getAuteurProjet(self):
        """Retourne l'auteur du projet.
        
        Returns:
            str: Auteur du projet.
        """
        return self.__auteurProjet
    
    # OK
    def getDate(self):
        """Retourne la date de création du projet.
        
        Returns:
            dt: Date de création du projet.
        """
        return self.__date
    
    # OK
    def getNomMagasin(self):
        """Retourne le nom du magasin.
        
        Returns:
            str: Nom du magasin.
        """
        return self.__nomMagasin
    
    # OK
    def getAdresse(self):
        """Retourne l'adresse du magasin.
        
        Returns:
            str: Adresse du magasin.
        """
        return self.__adresse
    
    # OK
    def getListeProduitsDispo(self):
        """Retourne la liste des produits disponibles dans le magasin.
        
        Returns:
            list: Liste des produits disponibles dans le magasin.
        """
        return self.__listeProduitsDispo
    
    # OK
    def getPlan(self):
        """Retourne le plan du magasin.
        
        Returns:
            Plan: Plan du magasin, représentant la disposition des cases.
        """
        return self.__plan
    
    # OK
    def setNomProjet(self, nomProjet: str):
        """Définit le nom du projet.
        
        Args:
            nomProjet (str): Nom du projet.
        """
        self.__nomProjet = nomProjet
    
    # OK
    def setAuteurProjet(self, auteurProjet: str):
        """Définit l'auteur du projet.
        
        Args:
            auteurProjet (str): Auteur du projet.
        """
        self.__auteurProjet = auteurProjet
    
    # OK
    def setDate(self, date: dt):
        """Définit la date de création du projet.
        
        Args:
            date (dt): Date de création du projet.
        """
        self.__date = date
    
    # OK
    def setNomMagasin(self, nomMagasin: str):
        """Définit le nom du magasin.
        
        Args:
            nomMagasin (str): Nom du magasin.
        """
        self.__nomMagasin = nomMagasin
    
    # OK
    def setAdresse(self, adresse: str):
        """Définit l'adresse du magasin.
        
        Args:
            adresse (str): Adresse du magasin.
        """
        self.__adresse = adresse
        
    # OK
    def setListeProduitsDispo(self, listeProduitsDispo: list):
        """Définit la liste des produits disponibles dans le magasin.
        
        Args:
            listeProduitsDispo (list): Liste des produits disponibles dans le magasin.
        """
        self.__listeProduitsDispo = listeProduitsDispo
    
    # OK
    def setPlan(self, plan: Plan):
        """Définit le plan du magasin.
        
        Args:
            plan (Plan): Plan du magasin, représentant la disposition des cases.
        """
        self.__plan = plan

    # OK mais est-ce que c'est utile ?
    def remplirMagasin(self):
        """Remplit le magasin avec des produits dans les rayons et des informations sur chaque case."""
        print("Remplissage du magasin...")
        self.__plan.remplirPlan()

    # à relire et surement à revoir
    def afficher_etat(self):
        """Affiche l'état du magasin, y compris les rayons, les obstacles et le point de départ."""
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