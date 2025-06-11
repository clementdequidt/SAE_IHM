from Case import Case
import heapq
import json
import random

class Plan():
    # OK
    def __init__(self, longueur: int, largeur: int):
        self.__longueur = longueur
        self.__largeur = largeur
        self.__cases = [[Case((i, j)) for i in range(longueur)] for j in range(largeur)]
    
    # OK
    def getLongueur(self):
        return self.__longueur
    
    # OK
    def getLargeur(self):
        return self.__largeur
    
    # OK
    def getCase(self, coord: tuple):
        if 0 <= coord[0] < self.__largeur and 0 <= coord[1] < self.__longueur:
            return self.__cases[coord[0]][coord[1]]
    
    # OK
    def setLongueur(self, longueur: int):
        self.__longueur = longueur
        
    # OK
    def setLargeur(self, largeur: int):
        self.__largeur = largeur
    
    # OK
    def regenererPlan(self):
        self.__cases = [[Case((i, j)) for i in range(self.__longueur)] for j in range(self.__largeur)]
    
    # OK
    def casesVoisines(self, case: Case):
        coord = case.getCoord()
        voisins = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            voisinCoord = (coord[0] + dx, coord[1] + dy)
            if 0 <= voisinCoord[0] < self.__largeur and 0 <= voisinCoord[1] < self.__longueur:
                voisins.append(self.__cases[voisinCoord[0]][voisinCoord[1]])
        return voisins
    
    # OK
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
        else:
            case.setItemsAccessible([])
    
    # OK
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
    
    # OK
    def remplirPlan(self):
        for i in range(self.__largeur):
            for j in range(self.__longueur):
                self.remplirCase((i, j))
    
    # OK
    def trouverDepart(self):
        for i in range(self.__largeur):
            for j in range(self.__longueur):
                case = self.__cases[i][j]
                if case.isDepart():
                    return case
        return None
    
    # # OK
    def trouverCasesPossiblesItem(self, item: str):
        casesPossibles = []
        for i in range(self.__largeur):
            for j in range(self.__longueur):
                case = self.__cases[i][j]
                if not case.isObstacle() and item in case.getItemsAccessible():
                    casesPossibles.append(case)
        return casesPossibles
    
    # à revoir car case plus proche du départ != case plus proche d'une autre case ? à tester sinon
    def trouverCasesAVisiter(self, listeCourses: list):
        casesAVisiter = []
        depart = self.trouverDepart()
        if depart is not None:
            for item in listeCourses:
                distanceMin = 0
                caseAVisiter = None
                for case in self.trouverCasesPossiblesItem(item):
                    chemin = self.plusCourtCheminCase(depart.getCoord(), case.getCoord())
                    if chemin:
                        distanceCase = len(chemin) - 1
                        if distanceCase < distanceMin or distanceMin == 0:
                            distanceMin = distanceCase
                            caseAVisiter = case
                if caseAVisiter is not None:
                    casesAVisiter.append(caseAVisiter)
        return casesAVisiter
    
    # OK mais à tester en condition réelle quand même
    def plusCourtCheminCase(self, depart: tuple, arrivee: tuple):
        if depart == arrivee:
            return [depart]
        
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
    
    # OK mais à tester en condition réelle quand même
    def plusCourtCheminListeCourses(self, listeCourses: list):
        cheminTotal = []
        casesAVisiter = self.trouverCasesAVisiter(listeCourses)
        caseActuelle = self.trouverDepart()
        
        for case in casesAVisiter:
            chemin = self.plusCourtCheminCase(caseActuelle.getCoord(), case.getCoord())
            if not chemin:
                print(f"Aucun chemin trouvé de {caseActuelle.getCoord()} à {case.getCoord()}.")
                continue
            if cheminTotal and chemin[0] == cheminTotal[-1]:
                cheminTotal.extend(chemin[1:])
            else:
                cheminTotal.extend(chemin)
            caseActuelle = case
        return cheminTotal
    
    # OK
    def listeCoursesAleatoire(self):
        with open('C:/Users/basti/Documents/SAE_IHM/Liste de produits-20250526/liste_produits.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        tous_les_produits = []
        for produits in data.values():
            tous_les_produits.extend(produits)

        taille_liste = random.randint(20, len(tous_les_produits))
        liste_aleatoire = random.sample(tous_les_produits, taille_liste)

        for produit in liste_aleatoire:
            print(produit)
        
        return liste_aleatoire