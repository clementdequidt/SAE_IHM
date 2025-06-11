import unittest
from Plan import Plan
from Case import Case

class TestPlan(unittest.TestCase):
    """Classe de test pour la classe Plan."""
    
    def setUp(self):
        """Initialise un plan de 5x5 cases pour les tests."""
        self.plateau = Plan(5, 5)

    def test_getters_setters(self):
        """Test les getters et setters pour la longueur et la largeur du plan."""
        self.assertEqual(self.plateau.getLongueur(), 3)
        self.assertEqual(self.plateau.getLargeur(), 3)
        self.plateau.setLongueur(4)
        self.plateau.setLargeur(5)
        self.assertEqual(self.plateau.getLongueur(), 4)
        self.assertEqual(self.plateau.getLargeur(), 5)

    def test_getCase(self):
        """Test la récupération d'une case par ses coordonnées."""
        case = self.plateau.getCase((1, 1))
        self.assertIsInstance(case, Case)
        self.assertIsNone(self.plateau.getCase((10, 10)))

    def test_regenererPlan(self):
        """Test la régénération du plan."""
        case_before = self.plateau.getCase((0, 0))
        self.plateau.regenererPlan()
        case_after = self.plateau.getCase((0, 0))
        self.assertNotEqual(case_before, case_after)

    def test_casesVoisines(self):
        """Test la récupération des cases voisines d'une case."""
        case = self.plateau.getCase((1, 1))
        voisins = self.plateau.casesVoisines(case)
        self.assertEqual(len(voisins), 4)

    def test_setItemsAccessible(self):
        """Test la mise à jour des items accessibles depuis une case."""
        self.plateau.getCase((1, 1)).setRayon(True)
        self.plateau.getCase((1, 1)).setItemsInRayon(['pomme'])
        self.plateau.setItemsAccessible((1, 1))
        self.assertIn('pomme', self.plateau.getCase((1, 1)).getItemsAccessible())

    def test_trouverDepart(self):
        """Test la recherche du point de départ dans le plan."""
        self.plateau.getCase((0, 0)).setDepart(True)
        depart = self.plateau.trouverDepart()
        self.assertEqual(depart.getCoord(), (0, 0))

    def test_trouverCasesPossiblesItem(self):
        """Test la recherche des cases possibles à visiter pour un item spécifique."""
        case = self.plateau.getCase((1, 1))
        case.setItemsAccessible(['pomme'])
        cases = self.plateau.trouverCasesPossiblesItem('pomme')
        self.assertIn(case, cases)

    def test_plusCourtCheminCase(self):
        """Test la recherche du plus court chemin entre 2 cases."""
        chemin = self.plateau.plusCourtCheminCase((0, 0), (2, 2))
        self.assertTrue((2, 2) in chemin)

    def test_plusCourtCheminCase_obstacle(self):
        """Test le plus court chemin entre 2 cases mais avec des obstacles."""
        self.plateau.getCase((1, 0)).setObstacle(True)
        self.plateau.getCase((0, 1)).setObstacle(True)
        chemin = self.plateau.plusCourtCheminCase((0, 0), (2, 2))
        self.assertEqual(chemin, [])

    def test_trouverCaseAVisiterItem(self):
        """Test la recherche d'une case à visiter pour un item spécifique."""
        self.plateau.getCase((0, 0)).setDepart(True)
        self.plateau.getCase((2, 2)).setItemsAccessible(['banane'])
        case = self.plateau.trouverCaseAVisiterItem(self.plateau.trouverDepart(), 'banane')
        self.assertEqual(case.getCoord(), (2, 2))

    def test_plusCourtCheminListeCourses(self):
        """Test la recherche du plus court chemin pour collecter tous les items d'une liste de courses."""
        self.plateau.getCase((0, 0)).setDepart(True)
        self.plateau.getCase((1, 1)).setItemsAccessible(['eau'])
        self.plateau.getCase((2, 2)).setItemsAccessible(['pain'])
        chemin = self.plateau.plusCourtCheminListeCourses(['eau', 'pain'])
        self.assertIn((0, 0), chemin)
        self.assertIn((1, 1), chemin)
        self.assertIn((2, 2), chemin)

if __name__ == '__main__':
    unittest.main()