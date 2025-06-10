from Case import Case

class Plan():
    def __init__(self, longueur: int, largeur: int):
        self.__longueur = longueur
        self.__largeur = largeur
        self.__cases = [[Case((i, j)) for i in range(longueur)] for j in range(largeur)]
    
    def getLongueur(self):
        return self.__longueur
    
    def getLargeur(self):
        return self.__largeur
    
    def getCase(self, coord: tuple):
        if 0 <= coord[0] < self.__largeur and 0 <= coord[1] < self.__longueur:
            return self.__cases[coord[0]][coord[1]]
    
    def setLongueur(self, longueur: int):
        self.__longueur = longueur
        
    def setLargeur(self, largeur: int):
        self.__largeur = largeur
    
    def regenererPlan(self):
        self.__cases = [[Case((i, j)) for i in range(self.__longueur)] for j in range(self.__largeur)]
    
    def casesVoisines(self, case: Case):
        coord = case.getCoord()
        voisins = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            voisinCoord = (coord[0] + dx, coord[1] + dy)
            if 0 <= voisinCoord[0] < self.__largeur and 0 <= voisinCoord[1] < self.__longueur:
                voisins.append(self.__cases[voisinCoord[0]][voisinCoord[1]])
        return voisins
    
    def setItemsAccessible(self, coord: tuple):
        if 0 <= coord[0] < self.__largeur and 0 <= coord[1] < self.__longueur:
            case = self.__cases[coord[0]][coord[1]]
            if not case.isObstacle():
                itemsAccessible = []
                if case.isRayon():
                    itemsAccessible = case.getItemsInRayon()
                else:
                    for caseAdj in self.casesVoisines(case):
                        if caseAdj.isRayon():
                            itemsAccessible.extend(caseAdj.getItemsInRayon())
            case.setItemsAccessible(itemsAccessible)
    
    def remplirCase(self, coord: tuple):
        if 0 <= coord[0] < self.__largeur and 0 <= coord[1] < self.__longueur:
            case = self.__cases[coord[0]][coord[1]]
            case.setDepart(input(f"Est-ce que la case {coord} est un point de départ ? (oui/non) ").strip().lower() == 'oui')
            case.setCaisse(input(f"Est-ce que la case {coord} est une caisse ? (oui/non) ").strip().lower() == 'oui')
            case.setRayon(input(f"Est-ce que la case {coord} est un rayon ? (oui/non) ").strip().lower() == 'oui')
            if case.isRayon():
                itemsInRayon = input(f"Quels sont les items dans le rayon de la case {coord} ? (séparés par des virgules) ").strip().split(',')
                itemsInRayon = [item.strip() for item in itemsInRayon if item.strip()]
                case.setItemsInRayon(itemsInRayon)
            case.setObstacle(input(f"Est-ce que la case {coord} est un obstacle ? (oui/non) ").strip().lower() == 'oui')
            self.setItemsAccessible(coord)
    
    def remplirPlan(self):
        for i in range(self.__largeur):
            for j in range(self.__longueur):
                self.remplirCase((i, j))
    
    def trouverCasesPossiblesItem(self, item: str):
        casesPossibles = []
        for i in range(self.__largeur):
            for j in range(self.__longueur):
                case = self.__cases[i][j]
                if not case.isObstacle() and item in case.getItemsAccessible():
                    casesPossibles.append(case)
        return casesPossibles
    
    def trouverCasesAVisiter(self, listeCourses: list):
        casesAVisiter = []
        for item in listeCourses:
            for case in self.trouverCasesPossiblesItem(item):
                for j in range(self.__longueur):
                    case = self.__cases[i][j]
                    if case.isRayon() and item in case.getItemsInRayon() and case not in casesAVisiter:
                        casesAVisiter.append(case)
        return casesAVisiter
    
    def plusCourtCheminCase(self, depart: tuple, case: tuple):
        pass
    
    def plusCourtCheminListeCourses(self, depart: tuple, listeCourses: list):
        casesAVisiter = self.trouverCasesAVisiter(listeCourses)