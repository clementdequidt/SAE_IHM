class Case():
    # OK
    def __init__(self, coord: tuple, depart: bool = False, caisse: bool = False, rayon: bool = False, itemsInRayon: list = [], obstacle: bool = False):
        self.__coord = coord
        self.__depart = depart
        self.__caisse = caisse
        self.__rayon = rayon
        self.__itemsInRayon = itemsInRayon
        self.__itemsAccessible: list = []
        self.__obstacle = obstacle
    
    # OK
    def getCoord(self):
        return self.__coord
    
    # OK
    def isDepart(self):
        return self.__depart
    
    # OK
    def isCaisse(self):
        return self.__caisse
    
    # OK
    def isRayon(self):
        return self.__rayon
    
    # OK
    def getItemsInRayon(self):
        return self.__itemsInRayon
    
    # OK
    def getItemsAccessible(self):
        return self.__itemsAccessible
    
    # OK
    def isObstacle(self):
        return self.__obstacle
    
    # OK
    def setCoord(self, coord: tuple):
        self.__coord = coord
        
    # OK
    def setDepart(self, depart: bool):
        self.__depart = depart
    
    # OK
    def setCaisse(self, caisse: bool):
        self.__caisse = caisse
    
    # OK
    def setRayon(self, rayon: bool):
        self.__rayon = rayon
    
    # OK
    def setItemsInRayon(self, itemsInRayon: list):
        self.__itemsInRayon = itemsInRayon
    
    # OK
    def setItemsAccessible(self, itemsAccessible: list):
        self.__itemsAccessible = itemsAccessible
    
    # OK
    def setObstacle(self, obstacle: bool):
        self.__obstacle = obstacle