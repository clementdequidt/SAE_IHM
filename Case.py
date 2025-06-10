class Case():
    
    def __init__(self, coord: tuple, depart: bool = False, caisse: bool = False, rayon: bool = False, itemsInRayon: list = [], obstacle: bool = False):
        self.__coord = coord
        self.__depart = depart
        self.__caisse = caisse
        self.__rayon = rayon
        self.__itemsInRayon = itemsInRayon
        self.__itemsAccessible: list = []
        self.__obstacle = obstacle
    
    def getCoord(self):
        return self.__coord
    
    def isDepart(self):
        return self.__depart
    
    def isCaisse(self):
        return self.__caisse
    
    def isRayon(self):
        return self.__rayon
    
    def getItemsInRayon(self):
        return self.__itemsInRayon
    
    def getItemsAccessible(self):
        return self.__itemsAccessible
    
    def isObstacle(self):
        return self.__obstacle
    
    def setCoord(self, coord: tuple):
        self.__coord = coord
        
    def setDepart(self, depart: bool):
        self.__depart = depart
        
    def setCaisse(self, caisse: bool):
        self.__caisse = caisse
        
    def setRayon(self, rayon: bool):
        self.__rayon = rayon
    
    def setItemsInRayon(self, itemsInRayon: list):
        self.__itemsInRayon = itemsInRayon
        
    def setItemsAccessible(self, itemsAccessible: list):
        self.__itemsAccessible = itemsAccessible
    
    def setObstacle(self, obstacle: bool):
        self.__obstacle = obstacle