from PyQt6.QtCore import QPointF

class ProduitManager:
    def __init__(self):
        self.produits_par_categorie = {}  # {catégorie: [produit1, produit2, ...]}
        self.selections_globales = {}     # {produit: True/False}
        self.positions_produits = {}      # {produit: {'x': x, 'y': y}}

        self.historique_positions = []    # [(produit, QPointF), ...]
        self.historique_index = -1

    def charger_depuis_json(self, data: dict):
        self.produits_par_categorie = data
        for cat, produits in data.items():
            for produit in produits:
                self.selections_globales[produit] = False

    def valider_selection(self):
        final = {}
        for produit, selected in self.selections_globales.items():
            if selected:
                for cat, produits in self.produits_par_categorie.items():
                    if produit in produits:
                        final.setdefault(cat, []).append(produit)
                        break
        return final

    def set_position(self, produit: str, point: QPointF, enregistrer=True):
        self.positions_produits[produit] = {'x': point.x(), 'y': point.y()}
        if enregistrer:
            del self.historique_positions[self.historique_index + 1:]
            self.historique_positions.append((produit, point))
            self.historique_index += 1

    def annuler(self):
        if self.historique_index >= 0:
            produit, _ = self.historique_positions[self.historique_index]
            self.positions_produits.pop(produit, None)
            self.historique_index -= 1
            return True
        return False

    def refaire(self):
        if self.historique_index + 1 < len(self.historique_positions):
            self.historique_index += 1
            produit, point = self.historique_positions[self.historique_index]
            self.set_position(produit, point, enregistrer=False)
            return True
        return False

    def charger_positions(self, positions: dict):
        self.positions_produits = positions.copy()
        self.historique_positions = [(k, QPointF(v['x'], v['y'])) for k, v in positions.items()]
        self.historique_index = len(self.historique_positions) - 1

    def exporter_positions(self):
        return self.positions_produits.copy()