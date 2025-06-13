#Fichier crée par Bastien COUSIN, Pierre DELDALLE, Clément DEQUIDT, Sébastien GROUÉ
from Case import Case
import heapq
import json
import random

class Plan():
    """Classe représentant le plan d'un magasin."""
    
    # OK
    def __init__(self, longueur: int, largeur: int):
        """Constructeur qui initialise un objet Plan et ses attributs.
        
        Args:
            longueur (int): Longueur du plan (nombre de cases en largeur).
            largeur (int): Largeur du plan (nombre de cases en hauteur).
        
        Attributes:
            __cases (list): Matrice représentant les cases du plan, chaque case étant une instance de la classe Case.
        """
        self.__longueur = longueur
        self.__largeur = largeur
        self.__cases = [[Case((i, j)) for j in range(largeur)] for i in range(longueur)]
    
    # OK
    def getLongueur(self):
        """Retourne la longueur du plan.
        
        Returns:
            int: Longueur du plan.
        """
        return self.__longueur
    
    # OK
    def getLargeur(self):
        """Retourne la largeur du plan.
        
        Returns:
            int: Largeur du plan.
        """
        return self.__largeur
    
    # OK
    def getCase(self, coord: tuple):
        """Retourne la case aux coordonnées spécifiées.
        
        Args:
            coord (tuple): Coordonnées de la case sous forme de tuple (x, y).
        
        Returns:
            Case: Instance de la classe Case correspondant aux coordonnées spécifiées, ou None si les coordonnées sont hors limites.
        """
        if 0 <= coord[0] < self.__longueur and 0 <= coord[1] < self.__largeur:
            return self.__cases[coord[0]][coord[1]]
        return None
    
    # OK
    def setLongueur(self, longueur: int):
        """Modifie la longueur du plan.
        
        Args:
            longueur (int): Nouvelle longueur du plan.
        """
        self.__longueur = longueur
        
    # OK
    def setLargeur(self, largeur: int):
        """Modifie la largeur du plan.
        
        Args:
            largeur (int): Nouvelle largeur du plan.
        """
        self.__largeur = largeur
    
    # OK
    def regenererPlan(self):
        """Regénère le plan en créant une nouvelle matrice de cases."""
        self.__cases = [[Case((i, j)) for j in range(self.__longueur)] for i in range(self.__largeur)]
    
    # OK
    def casesVoisines(self, case: Case):
        """Retourne les 4 cases voisines d'une case donnée.
        
        Args:
            case (Case): Instance de la classe Case dont on veut les cases voisines.
        
        Returns:
            list: Liste des cases voisines de la case donnée.
        """
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
        """Met à jour les items accessibles depuis la case aux coordonnées spécifiées.
        
        Args:
            coord (tuple): Coordonnées de la case sous forme de tuple (x, y).
        """
        if 0 <= coord[0] < self.__longueur and 0 <= coord[1] < self.__largeur:
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
        """Remplit les informations d'une case aux coordonnées spécifiées en demandant à l'utilisateur de saisir les informations pour chaque case.
        
        Args:
            coord (tuple): Coordonnées de la case sous forme de tuple (x, y).
        """
        if 0 <= coord[0] < self.__longueur and 0 <= coord[1] < self.__largeur:
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
        """Remplit toutes les cases du plan."""
        for i in range(self.__longueur):
            for j in range(self.__largeur):
                self.remplirCase((i, j))
    
    # OK
    def trouverDepart(self):
        """Trouve la case de départ dans le plan.
        
        Returns:
            Case: Instance de la classe Case qui est le point de départ, ou None si aucun point de départ n'est trouvé.
        """
        for i in range(self.__longueur):
            for j in range(self.__largeur):
                case = self.__cases[i][j]
                if case.isDepart():
                    return case
        return None
    
    # OK
    def trouverCasesPossiblesItem(self, item: str):
        """Trouve toutes les cases accessibles depuis lesquels un item spécifique est accessible.
        
        Args:
            item (str): Nom de l'item à rechercher.
        
        Returns:
            list: Liste des cases accessibles depuis lesquels l'item spécifié est accessible.
        """
        casesPossibles = []
        for i in range(self.__longueur):
            for j in range(self.__largeur):
                case = self.__cases[i][j]
                if not case.isObstacle() and item in case.getItemsAccessible():
                    casesPossibles.append(case)
        return casesPossibles
    
    # OK
    def trouverCaseAVisiterItem(self, depart: Case, item: str):
        """Trouve la case la plus proche à visiter pour prendre un item spécifique à partir d'une case de départ quelconque.
        
        Args:
            depart (Case): Case de départ quelconque à partir de laquelle on cherche la case à visiter.
            item (str): Nom de l'item à rechercher.
        
        Returns:
            Case: Instance de la classe Case qui est la plus proche de la case de départ et accessible pour l'item spécifié, ou None si aucune case n'est trouvée.
        """
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
            return caseAVisiter
        return None
    
    # OK
    def trouverCaissesPossibles(self):
        """Trouve toutes les caisses dans le plan.
        
        Returns:
            list: Liste des cases qui sont des caisses.
        """
        caissesPossibles = []
        for i in range(self.__longueur):
            for j in range(self.__largeur):
                case = self.__cases[i][j]
                if case.isCaisse():
                    caissesPossibles.append(case)
        return caissesPossibles
    
    # OK mais à tester en condition réelle quand même
    def trouverCaisseAVisiter(self, depart: Case):
        """Trouve la caisse la plus proche à visiter à partir d'une case de départ quelconque.
        
        Args:
            depart (Case): Case de départ quelconque à partir de laquelle on cherche la caisse à visiter.
        
        Returns:
            Case: Instance de la classe Case qui est la plus proche de la case de départ et accessible, ou None si aucune caisse n'est trouvée.
        """
        distanceMin = 0
        caisseAVisiter = None
        for caisse in self.trouverCaissesPossibles():
            chemin = self.plusCourtCheminCase(depart.getCoord(), caisse.getCoord())
            if chemin:
                distanceCaisse = len(chemin) - 1
                if distanceCaisse < distanceMin or distanceMin == 0:
                    distanceMin = distanceCaisse
                    caisseAVisiter = caisse
        if caisseAVisiter is not None:
            return caisseAVisiter
        return None
    
    # OK mais à tester en condition réelle quand même
    def plusCourtCheminCase(self, depart: tuple, arrivee: tuple):
        """Trouve le plus court chemin entre deux cases spécifiées par leurs coordonnées.
        
        Args:
            depart (tuple): Coordonnées de la case de départ sous forme de tuple (x, y).
            arrivee (tuple): Coordonnées de la case d'arrivée sous forme de tuple (x, y).
        
        Returns:
            list: Liste des coordonnées du chemin le plus court de la case de départ à la case d'arrivée, ou une liste vide si aucun chemin n'est trouvé.
        """
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
        """Trouve le plus court chemin pour collecter les items d'une liste de courses à partir du point de départ jusqu'à la caisse.
        
        Args:
            listeCourses (list): Liste des items à collecter.
        
        Returns:
            list: Liste des coordonnées du chemin le plus court pour collecter les items de la liste de courses, en passant par la caisse à la fin.
            dict: Dictionnaire des positions des items collectés, avec les coordonnées comme clés et les listes d'items comme valeurs.
        """
        cheminTotal = []
        positionsItems = {}
        caseActuelle = self.trouverDepart()
        
        for item in listeCourses:
            caseAVisiter = self.trouverCaseAVisiterItem(caseActuelle, item)
            if caseAVisiter.getCoord() not in positionsItems:
                positionsItems[caseAVisiter.getCoord()] = [item]
            else:
                positionsItems[caseAVisiter.getCoord()].append(item)
            chemin = self.plusCourtCheminCase(caseActuelle.getCoord(), caseAVisiter.getCoord())
            if not chemin:
                print(f"Aucun chemin trouvé de {caseActuelle.getCoord()} à {caseAVisiter.getCoord()}.")
                continue
            if cheminTotal and chemin[0] == cheminTotal[-1]:
                cheminTotal.extend(chemin[1:])
            else:
                cheminTotal.extend(chemin)
            caseActuelle = caseAVisiter

        caseAVisiter = self.trouverCaisseAVisiter(caseActuelle)
        if caseAVisiter is None:
            print("Aucune caisse trouvée.")
            return cheminTotal, positionsItems
        chemin = self.plusCourtCheminCase(caseActuelle.getCoord(), caseAVisiter.getCoord())
        if not chemin:
            print(f"Aucun chemin trouvé de {caseActuelle.getCoord()} à {caseAVisiter.getCoord()}.")
        if cheminTotal and chemin[0] == cheminTotal[-1]:
            cheminTotal.extend(chemin[1:])
        else:
            cheminTotal.extend(chemin)

        return cheminTotal, positionsItems
    
    # OK
    def listeCoursesAleatoire(self):
        """Génère une liste de courses aléatoire à partir des produits disponibles dans le magasin pour faire des tests.
        
        Returns:
            list: Liste de course aléatoire.
        """
        with open('liste_produits.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        tous_les_produits = []
        for produits in data.values():
            tous_les_produits.extend(produits)

        taille_liste = random.randint(20, len(tous_les_produits))
        liste_aleatoire = random.sample(tous_les_produits, taille_liste)

        for produit in liste_aleatoire:
            print(produit)
        
        return liste_aleatoire