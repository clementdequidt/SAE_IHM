#Fichier crée par Bastien COUSIN, Pierre DELDALLE, Clément DEQUIDT, Sébastien GROUÉ
class Case():
    """Classe représentant une case d'un plan de magasin."""
    
    def __init__(self, coord: tuple, depart: bool = False, caisse: bool = False, rayon: bool = False, itemsInRayon: list = [], obstacle: bool = False):
        """Constructeur qui initialise un objet Case et ses attributs.
        
        Args:
            coord (tuple): Coordonnées de la case sous forme de tuple (x, y).
            depart (bool): Indique si la case est un point de départ. Par défaut, False.
            caisse (bool): Indique si la case est une caisse. Par défaut, False.
            rayon (bool): Indique si la case est un rayon. Par défaut, False.
            itemsInRayon (list): Liste des items présents dans le rayon si la case en est un. Par défaut, une liste vide.
            obstacle (bool): Indique si la case est un obstacle qui bloque la route dans le magasin. Par défaut, False.
        """
        self.__coord = coord
        self.__depart = depart
        self.__caisse = caisse
        self.__rayon = rayon
        self.__itemsInRayon = itemsInRayon
        self.__itemsAccessible: list = []
        self.__obstacle = obstacle
    
    # OK
    def getCoord(self):
        """Retourne les coordonnées de la case.
        
        Returns:
            tuple: Coordonnées de la case sous forme de tuple (x, y).
        """
        return self.__coord
    
    # OK
    def isDepart(self):
        """Indique si la case est un point de départ.
        
        Returns:
            bool: True si la case est un point de départ, False sinon.
        """
        return self.__depart
    
    # OK
    def isCaisse(self):
        """Indique si la case est une caisse.
        
        Returns:
            bool: True si la case est une caisse, False sinon.
        """
        return self.__caisse
    
    # OK
    def isRayon(self):
        """Indique si la case est un rayon.
        
        Returns:
            bool: True si la case est un rayon, False sinon.
        """
        return self.__rayon
    
    # OK
    def getItemsInRayon(self):
        """Retourne la liste des items présents dans le rayon de la case.
        
        Returns:
            list: Liste des items présents dans le rayon de la case.
        """
        return self.__itemsInRayon
    
    # OK
    def getItemsAccessible(self):
        """Retourne la liste des items accessibles depuis cette case.
        
        Returns:
            list: Liste des items accessibles depuis cette case.
        """
        return self.__itemsAccessible
    
    # OK
    def isObstacle(self):
        """Indique si la case est un obstacle.
        
        Returns:
            bool: True si la case est un obstacle, False sinon.
        """
        return self.__obstacle
    
    # OK
    def setCoord(self, coord: tuple):
        """Définit les coordonnées de la case.
        
        Args:
            coord (tuple): Coordonnées de la case sous forme de tuple (x, y).
        """
        self.__coord = coord
        
    # OK
    def setDepart(self, depart: bool):
        """Définit si la case est un point de départ.
        
        Args:
            depart (bool): True si la case est un point de départ, False sinon.
        """
        self.__depart = depart
    
    # OK
    def setCaisse(self, caisse: bool):
        """Définit si la case est une caisse.
        
        Args:
            caisse (bool): True si la case est une caisse, False sinon.
        """
        self.__caisse = caisse
    
    # OK
    def setRayon(self, rayon: bool):
        """Définit si la case est un rayon.
        
        Args:
            rayon (bool): True si la case est un rayon, False sinon.
        """
        self.__rayon = rayon
    
    # OK
    def setItemsInRayon(self, itemsInRayon: list):
        """Définit la liste des items présents dans le rayon de la case.
        
        Args:
            itemsInRayon (list): Liste des items présents dans le rayon de la case.
        """
        self.__itemsInRayon = itemsInRayon
    
    # OK
    def setItemsAccessible(self, itemsAccessible: list):
        """Définit la liste des items accessibles depuis cette case.
        
        Args:
            itemsAccessible (list): Liste des items accessibles depuis cette case.
        """
        self.__itemsAccessible = itemsAccessible
    
    # OK
    def setObstacle(self, obstacle: bool):
        """Définit si la case est un obstacle.
        
        Args:
            obstacle (bool): True si la case est un obstacle, False sinon.
        """
        self.__obstacle = obstacle