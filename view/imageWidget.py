from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class ImageWidget(QGraphicsView):
    produitPlaceSignal = pyqtSignal(str, QPointF)
    cellTypeChange = pyqtSignal(QPointF, str) 

    # Taille d'une case
    CELL_SIZE = 51

    def __init__(self, chemin: str):
        super().__init__()

        self.zoom = 0 
        self.empty = True
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.pixmapItem = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmapItem)
        
        self.gridCells = []
        self.productTextItems = {}
        self.productPositionsHistory = [] 
        self.historyIndex = -1 

        self.cellTypes = {}
        self.cellRectangleItems = {} 
        
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        self.setAcceptDrops(True)

        pixmap = QPixmap(chemin)
        if pixmap.isNull():
            label = QLabel(f"Image non trouvée : {chemin}") 
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scene.addWidget(label)
        else:
            self.setPixmap(pixmap) 

    def setPixmap(self, pixmap: QPixmap):
        self.zoom = 0
        self.pixmapItem.setPixmap(pixmap)
        
        self.scene.setSceneRect(QRectF(pixmap.rect()))
        
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.empty = False
        self.drawGridOverlay()
        
        self.productPositionsHistory = []
        self.historyIndex = -1
        self.cellTypes.clear() 
        self.miseAJourVisuelCell() 

    def drawGridOverlay(self):
        # Supprime les cellules de la grille
        for cell in self.gridCells:
            self.scene.removeItem(cell)
        self.gridCells.clear()
        self.cellRectangleItems.clear() 

        #Pour reprendre la taille de l'image
        imageWidth = self.pixmapItem.pixmap().width()
        imageHeight = self.pixmapItem.pixmap().height()

        gridColorBorder = QColor(255, 0, 0, 100)
        gridPen = QPen(gridColorBorder)
        gridPen.setWidth(2)

        # Crée une grille rectangulaire par-dessus l’image
        for y in range(0, imageHeight, self.CELL_SIZE):
            for x in range(0, imageWidth, self.CELL_SIZE):
                rectangleItem = QGraphicsRectItem(x, y, self.CELL_SIZE, self.CELL_SIZE)
                rectangleItem.setPen(gridPen)
                self.scene.addItem(rectangleItem)
                self.gridCells.append(rectangleItem)
                self.cellRectangleItems[(x, y)] = rectangleItem 
                rectangleItem.setZValue(1) 

        self.pixmapItem.setZValue(0)
        self.miseAJourVisuelCell() 

    def miseAJourVisuelCell(self):
        """Met à jour l'apparence visuelle de toutes les cellules de la grille en fonction de leur type."""
        for (x, y), rectangleItem in self.cellRectangleItems.items():
            cellType = self.cellTypes.get((x, y))
            pen = QPen(QColor(255, 0, 0, 100)) 
            pen.setWidth(2)
            
            brush = QBrush(Qt.BrushStyle.NoBrush)
            if cellType == "entrée":
                brush = QBrush(QColor(0, 255, 0, 100)) # Vert pour entrée
            elif cellType == "obstacle":
                brush = QBrush(QColor(255, 0, 0, 100)) # Rouge pour obstacle
            elif cellType == "rayon":
                brush = QBrush(QColor(0, 0, 255, 100)) # Bleu pour rayon
            elif cellType == "caisse":
                brush = QBrush(QColor(255, 255, 0, 100)) # Jaune pour caisse
            
            rectangleItem.setPen(pen)
            rectangleItem.setBrush(brush)
            rectangleItem.setZValue(2)

    def setCellType(self, gridX: int, gridY: int, cellType: str):
        """Définit le type d'une cellule et met à jour sa représentation visuelle."""
        if (gridX, gridY) in self.cellRectangleItems:
            self.cellTypes[(gridX, gridY)] = cellType
            self.miseAJourVisuelCell()
            self.cellTypeChange.emit(QPointF(gridX, gridY), cellType) 

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            scenePos = self.mapToScene(event.pos())
            
            # Calculer les coordonnées en haut à gauche de la cellule de la grille cliquée
            gridX = (int(scenePos.x()) // self.CELL_SIZE) * self.CELL_SIZE
            gridY = (int(scenePos.y()) // self.CELL_SIZE) * self.CELL_SIZE

            self.showContextMenu(gridX, gridY, event.globalPosition().toPoint())
        else:
            super().mousePressEvent(event) 

    def showContextMenu(self, gridX: int, gridY: int, globalPos: QPoint):
        """Affiche un menu contextuel pour définir les types de cellules."""
        menu = QMenu(self)

        actionEntree = menu.addAction("Définir comme Entrée Magasin")
        actionObstacle = menu.addAction("Définir comme Obstacle")
        actionRayon = menu.addAction("Définir comme Rayon")
        actionCaisse = menu.addAction("Définir comme Caisse")
        
        # Ajouter une option pour effacer le type de cellule
        actionEffacer = menu.addAction("Effacer le type de cellule")

        action = menu.exec(globalPos)

        if action == actionEntree:
            self.setCellType(gridX, gridY, "entrée")
        elif action == actionObstacle:
            self.setCellType(gridX, gridY, "obstacle")
        elif action == actionRayon:
            self.setCellType(gridX, gridY, "rayon")
        elif action == actionCaisse:
            self.setCellType(gridX, gridY, "caisse")
        elif action == actionEffacer:
            if (gridX, gridY) in self.cellTypes:
                del self.cellTypes[(gridX, gridY)] 
                self.miseAJourVisuelCell() 
                self.cellTypeChange.emit(QPointF(gridX, gridY), "clear") 
            
    def placerProduit(self, productName: str, x: float, y: float, recordHistory=True):
        if productName in self.productTextItems:
            self.scene.removeItem(self.productTextItems[productName])
            del self.productTextItems[productName]

        textItem = QGraphicsTextItem(productName)
        textItem.setDefaultTextColor(QColor("red"))
        textItem.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        textItem.setPos(x - textItem.boundingRect().width() / 2,
                         y - textItem.boundingRect().height() / 2)

        textItem.setZValue(3)
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