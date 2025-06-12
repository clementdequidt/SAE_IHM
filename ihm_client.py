#VUE_CLIENT

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QStatusBar, \
                            QLabel, QTextEdit, QFileDialog, QDockWidget
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap, QMouseEvent, QWheelEvent, QPainter
from PyQt6.QtCore import Qt, QPointF, QRectF


# --- class widget: hérite de QLabel ------------------------------------------
class Image(QGraphicsView):
    def __init__(self, chemin: str):
        super().__init__()

        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._pixmap_item = QGraphicsPixmapItem()
        self._scene.addItem(self._pixmap_item)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        self.setPixmap(QPixmap(chemin))

    def setPixmap(self, pixmap: QPixmap):
        self._zoom = 0
        self._pixmap_item.setPixmap(pixmap)
        self._scene.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._empty = False

    def wheelEvent(self, event: QWheelEvent):
        if self._empty:
            return

        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
            self._zoom += 1
        else:
            zoom_factor = zoom_out_factor
            self._zoom -= 1

        if self._zoom < -10:
            self._zoom = -10
            return
        if self._zoom > 30:
            self._zoom = 30
            return

        self.scale(zoom_factor, zoom_factor)



# -----------------------------------------------------------------------------
# --- class FenetreAppli
# -----------------------------------------------------------------------------
class FenetreAppli(QMainWindow):
    def __init__(self, chemin: str = None):
        super().__init__()
        self.__chemin = chemin
        
        self.setWindowTitle("test_ihm_client")
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen_geometry)

        # widget central
        if not chemin is None:
            self.affiche_image()

        # dock
        self.dock = QDockWidget('Liste de course')
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        self.dock.setMaximumWidth(400)
        self.text_edit = QTextEdit()
        self.dock.setWidget(self.text_edit)
        

        # barre d'état
        self.barre_etat = QStatusBar()
        self.setStatusBar(self.barre_etat)
        self.barre_etat.showMessage("L'application est démarrée...", 2000)

        # barre de menu
        menu_bar = self.menuBar()

        menu_fichier = menu_bar.addMenu('&Fichier')
        menu_edition = menu_bar.addMenu('&Edition')
        menu_aide = menu_bar.addMenu('&Aide')

        menu_fichier.addAction('Nouveau', self.nouveau)
        menu_fichier.addAction('Ouvrir', self.ouvrir)
        menu_fichier.addAction('Enregistrer', self.enregistrer)
        menu_fichier.addSeparator()
        menu_fichier.addAction('Quitter', self.destroy)







        self.showMaximized()


    def nouveau(self):
        self.barre_etat.showMessage('Créer un nouveau ....', 2000)
        boite = QFileDialog()
        chemin, validation = boite.getOpenFileName(directory = sys.path[0])
        if validation:
            self.__chemin = chemin


    def ouvrir(self):
        self.barre_etat.showMessage('Ouvrir un nouveau....', 2000)
        boite = QFileDialog()
        chemin, validation = boite.getOpenFileName(directory = sys.path[0])
        if validation:
            self.__chemin = chemin
            self.affiche_image()


    def enregistrer(self):
        self.barre_etat.showMessage('Enregistrer....', 2000 )
        boite = QFileDialog()
        chemin, validation = boite.getSaveFileName(directory = sys.path[0])
        if validation:
            self.__chemin = chemin

        
    def affiche_image(self):
        self.image = Image(self.__chemin)
        self.setCentralWidget(self.image)


# --- main --------------------------------------------------------------------
if __name__ == "__main__":

    # création d'une QApplication
    app = QApplication(sys.argv)

    # ouverture d'un fichier de style (il y en a d'autres...)

    # récupération du contenu et application du style


    # # création de la fenêtre de l'application
    fenetre = FenetreAppli(sys.path[0] + '/Quadrillage_Final.jpg')

    # lancement de l'application
    sys.exit(app.exec())