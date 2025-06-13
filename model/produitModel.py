from PyQt6.QtCore import QPointF

class ProduitManager:
    def __init__(self):
        self.produitsParCategorie = {}  # {catégorie: [produit1, produit2, ...]}
        self.selectionsGlobales = {}     # {produit: True/False}
        self.positionsProduits = {}      # {produit: {'x': x, 'y': y}}

        self.historiquePositions = []    # [(produit, QPointF), ...]
        self.historiqueIndex = -1

    def chargerDepuisJson(self, data: dict):
        self.produitsParCategorie = data
        for cat, produits in data.items():
            for produit in produits:
                self.selectionsGlobales[produit] = False

    def validerSelection(self):
        final = {}
        for produit, selected in self.selectionsGlobales.items():
            if selected:
                for cat, produits in self.produitsParCategorie.items():
                    if produit in produits:
                        final.setdefault(cat, []).append(produit)
                        break
        return final

    def setPosition(self, produit: str, point: QPointF, enregistrer=True):
        self.positionsProduits[produit] = {'x': point.x(), 'y': point.y()}
        if enregistrer:
            del self.historiquePositions[self.historiqueIndex + 1:]
            self.historiquePositions.append((produit, point))
            self.historiqueIndex += 1

    def annuler(self):
        if self.historiqueIndex >= 0:
            produit, _ = self.historiquePositions[self.historiqueIndex]
            self.positionsProduits.pop(produit, None)
            self.historiqueIndex -= 1
            return True
        return False

    def refaire(self):
        if self.historiqueIndex + 1 < len(self.historiquePositions):
            self.historiqueIndex += 1
            produit, point = self.historiquePositions[self.historiqueIndex]
            self.setPosition(produit, point, enregistrer=False)
            return True
        return False

    def chargerPositions(self, positions: dict):
        self.positionsProduits = positions.copy()
        self.historiquePositions = [(k, QPointF(v['x'], v['y'])) for k, v in positions.items()]
        self.historiqueIndex = len(self.historiquePositions) - 1

    def exporterPositions(self):
        return self.positionsProduits.copy()