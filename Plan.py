from Case import Case
import heapq

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
    
    def trouverDepart(self):
        for i in range(self.__largeur):
            for j in range(self.__longueur):
                case = self.__cases[i][j]
                if case.isDepart():
                    return case
        return None
    
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
        depart = self.trouverDepart()
        if depart is not None:
            for item in listeCourses:
                distanceMin = 0
                caseAVisiter = None
                for case in self.trouverCasesPossiblesItem(item):
                    distanceCase = len(self.plusCourtCheminCase(depart, case.getCoord()) - 1)
                    if distanceCase < distanceMin or distanceMin == 0:
                        distanceMin = distanceCase
                        caseAVisiter = case
                casesAVisiter.append(case)
        return casesAVisiter
    
    def plusCourtCheminCase(self, depart: tuple, arrivee: tuple):
        distances = {(i,j): float('inf') for i in range(self.__largeur) for j in range(self.__longueur)}
        distances[depart] = 0
        predecesseurs = {}
        file = [(0, depart)]
        
        while file:
            dist_actuelle, coord_actuelle = heapq.heappop(file)
            if coord_actuelle == arrivee:
                break
            
            case_actuelle = self.getCase(coord_actuelle)
            if case_actuelle.isObstacle():
                continue
        
            for voisin in self.casesVoisines(case_actuelle):
                coord_voisin = voisin.getCoord()
                if voisin.isObstacle():
                    continue
                nouvelle_distance = dist_actuelle + 1
                if nouvelle_distance < distances[coord_voisin]:
                    distances[coord_voisin] = nouvelle_distance
                    predecesseurs[coord_voisin] = coord_actuelle
                    heapq.heappush(file, (nouvelle_distance, coord_voisin))
                
        chemin = []
        courant = arrivee
        if courant not in predecesseurs:
            return []
        while courant != depart:
            chemin.append(courant)
            courant = predecesseurs[courant]
        chemin.append(depart)
        chemin.reverse()
        return chemin  
        
    
    def plusCourtCheminListeCourses(self, depart: tuple, listeCourses: list):
        casesAVisiter = self.trouverCasesAVisiter(listeCourses)