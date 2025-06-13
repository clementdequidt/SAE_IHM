import os
from PyQt6.QtWidgets import QStackedWidget
from view.pageQuestionnaire import PageQuestionnaire
from view.choisirProduits import ChoisirProduits
from view.fenetreAppli import FenetreAppli

class AppMultiPages(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.pageQuestionnaire = PageQuestionnaire(self.allerAChoisirProduits)
        self.addWidget(self.pageQuestionnaire)  # index 0

        self.choisirProduits = ChoisirProduits()
        self.choisirProduits.selectionValidee.connect(self.allerAFenetreAppli)
        self.addWidget(self.choisirProduits) # index 1

        self.fenetreAppli = None

        self.setCurrentIndex(0)

    def allerAChoisirProduits(self):
        self.setCurrentIndex(1)
        self.choisirProduits.chargerProduits()

    def allerAFenetreAppli(self, produitsSelectionnes: dict):
        cheminImage = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../ressources/Quadrillage_Final.jpg')
        questionnaireData = self.pageQuestionnaire.getQuestionnaireData()

        if self.fenetreAppli is None:
            self.fenetreAppli = FenetreAppli(
                chemin=cheminImage,
                produitsSelectionnes=produitsSelectionnes,
                questionnaireData=questionnaireData
            )
            self.addWidget(self.fenetreAppli)  # index 2
        else:
            self.fenetreAppli.produitsSelectionnes = produitsSelectionnes
            self.fenetreAppli.questionnaireData = questionnaireData
            self.fenetreAppli.afficherProduitsDansDock()
            self.fenetreAppli.positionsProduits.clear()
            self.fenetreAppli.imageViewer.productPositionsHistory = []
            self.fenetreAppli.imageViewer.historyIndex = -1
            for item in list(self.fenetreAppli.imageViewer.productTextItems.values()):
                self.fenetreAppli.imageViewer.scene.removeItem(item)
            self.fenetreAppli.imageViewer.productTextItems.clear()
            self.fenetreAppli.imageViewer.drawGridOverlay()
            self.fenetreAppli.mettreAJourMagasin()
            self.fenetreAppli.mettreAJourDerniereAction()

        self.setCurrentIndex(2)