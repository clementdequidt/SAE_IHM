import unittest
from Plan import Plan

class TestPlusCourtCheminCase(unittest.TestCase):

    def setUp(self):
        # Crée un plateau 5x5 vide sans obstacle
        self.plateau = Plan(5, 5)
    
    def test_depart_egal_arrivee(self):
        chemin = self.plateau.plusCourtCheminCase((2, 2), (2, 2))
        self.assertEqual(chemin, [(2, 2)])

    def test_chemin_simple(self):
        chemin = self.plateau.plusCourtCheminCase((0, 0), (0, 1))
        self.assertEqual(chemin, [(0, 0), (0, 1)])

    def test_chemin_avec_obstacle(self):
        self.plateau.getCase((0, 1)).setObstacle(True)
        chemin = self.plateau.plusCourtCheminCase((0, 0), (0, 2))
        # Le chemin doit contourner l’obstacle ou être vide si impossible
        self.assertNotIn((0, 1), chemin)

    def test_arrivee_inatteignable(self):
        # Entoure (2,2) d'obstacles
        for coord in [(1, 2), (2, 1), (2, 3), (3, 2)]:
            self.plateau.getCase(coord).setObstacle(True)
        chemin = self.plateau.plusCourtCheminCase((0, 0), (2, 2))
        self.assertEqual(chemin, [])

if __name__ == '__main__':
    unittest.main()