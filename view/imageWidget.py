from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class ImageWidget(QGraphicsView):
    produitPlaceSignal = pyqtSignal(str, QPointF)

    #Taille d'une case
    CELL_SIZE = 51

    def __init__(self, chemin: str):
        super().__init__()

        self.zoom = 0 # Le zoom
        self.empty = True
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        #Pour afficher l'image
        self.pixmapItem = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmapItem)
        
        #stocker les cellules de la case
        self.gridCells = []
        self.productTextItems = {}
        self.productPositionsHistory = [] 
        self.historyIndex = -1 

        #Configure le point de zoom 
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        #Cache les barres de défilement
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        #Accepte le drag and drop
        self.setAcceptDrops(True)

        #Pour changer l'image grâce au chemin du fichier
        pixmap = QPixmap(chemin)
        if pixmap.isNull():
            label = QLabel(f"Image non trouvée : {chemin}") #Si le chemin de l'image n'est pas trouvé
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scene.addWidget(label)
        else:
            self.setPixmap(pixmap) #Sinon on affiche l'image

    def setPixmap(self, pixmap: QPixmap):
        #Met le zoom a zero
        self.zoom = 0
        self.pixmapItem.setPixmap(pixmap)
        
        #Définit la taille de la scène à celle de l’image
        self.scene.setSceneRect(QRectF(pixmap.rect()))
        
        #Pour mettre l'image dans la fenêtre
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.empty = False
        self.drawGridOverlay()
        
        #Remettre a vide l'historique
        self.ProductPositionsHistory = []
        self.historyIndex = -1

    def drawGridOverlay(self):
        
        # Supprime les cellules de la grille
        for cell in self.gridCells:
            self.scene.removeItem(cell)
        self.gridCells.clear()

        #Pour reprendre la taille de l'image
        imageWidth = self.pixmapItem.pixmap().width()
        imageHeight = self.pixmapItem.pixmap().height()

        gridColorBorder = QColor(255, 0, 0, 100)
        gridPen = QPen(gridColorBorder)
        gridPen.setWidth(2)

        # Crée une grille rectangulaire par-dessus l’image
        for y in range(0, imageHeight, self.CELL_SIZE):
            for x in range(0, imageWidth, self.CELL_SIZE):
                rectItem = QGraphicsRectItem(x, y, self.CELL_SIZE, self.CELL_SIZE)
                rectItem.setPen(gridPen)
                self.scene.addItem(rectItem)
                self.gridCells.append(rectItem)
                rectItem.setZValue(1) #Pour mettre la grille par dessus notre image

        self.pixmapItem.setZValue(0)

    def placerProduit(self, productName: str, x: float, y: float, recordHistory=True):
        if productName in self.productTextItems:
            self.scene.removeItem(self.productTextItems[productName])
            del self.productTextItems[productName]

        textItem = QGraphicsTextItem(productName)
        textItem.setDefaultTextColor(QColor("red"))
        textItem.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        textItem.setPos(x - textItem.boundingRect().width() / 2,
                         y - textItem.boundingRect().height() / 2)

        textItem.setZValue(2)
        self.scene.addItem(textItem)
        self.productTextItems[productName] = textItem

        if recordHistory:
            del self.productPositionsHistory[self.historyIndex + 1:]
            self.productPositionsHistory.append((productName, QPointF(x, y)))
            self.historyIndex += 1

    def retirerProduit(self, productName: str):
        if productName in self.productTextItems:
            self.scene.removeItem(self.productTextItems[productName])
            del self.productTextItems[productName]

    def enleverDerniereAction(self):
        if self.historyIndex >= 0:
            lastAction = self.productPositionsHistory[self.historyIndex]
            productNameToRemove = lastAction[0]
            self.retirerProduit(productNameToRemove)
            self.historyIndex -= 1
            self.produits()
            return True
        return False

    def rajouterDerniereAction(self):
        if self.historyIndex + 1 < len(self.productPositionsHistory):
            self.historyIndex += 1
            actionToRedo = self.productPositionsHistory[self.historyIndex]
            self.placerProduit(actionToRedo[0], actionToRedo[1].x(), actionToRedo[1].y(), recordHistory=False)
            return True
        return False

    def produits(self):
        for productItem in list(self.productTextItems.values()):
            self.scene.removeItem(productItem)
        self.productTextItems.clear()

        for i in range(self.historyIndex + 1):
            productName, position = self.productPositionsHistory[i]
            self.placerProduit(productName, position.x(), position.y(), recordHistory=False)


    def wheelEvent(self, event: QWheelEvent):
        if self.empty:
            return

        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
            self.zoom += 1
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= 1

        if self.zoom < -10:
            self.zoom = -10
            return
        if self.zoom > 30:
            self.zoom = 30
            return

        self.scale(zoomFactor, zoomFactor)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasText():
            productName = event.mimeData().text()
            scenePos = self.mapToScene(event.position().toPoint())

            gridX = (int(scenePos.x()) // self.CELL_SIZE) * self.CELL_SIZE
            gridY = (int(scenePos.y()) // self.CELL_SIZE) * self.CELL_SIZE

            centerX = gridX + self.CELL_SIZE / 2
            centerY = gridY + self.CELL_SIZE / 2

            self.placerProduit(productName, centerX, centerY, recordHistory=True)

            event.acceptProposedAction()
            self.produitPlaceSignal.emit(productName, QPointF(centerX, centerY))
        else:
            event.ignore()