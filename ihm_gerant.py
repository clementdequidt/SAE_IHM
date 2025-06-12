import sys
import platform
import json
import os
import ControlleurGerant

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QMessageBox, QTextEdit, QDockWidget, QStackedWidget, QStatusBar, QFileDialog, QDateEdit, QScrollArea, QCheckBox, QListWidget, QListWidgetItem,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsRectItem
)
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QIcon, QDrag, QMouseEvent, QWheelEvent, QPainter, QBrush, QColor, QFont, QPen, QDragMoveEvent, QDragLeaveEvent
from PyQt6.QtCore import Qt, QDate, QPointF, QRectF, pyqtSignal, QMimeData, QCoreApplication

# --- Détection du thème système ---
def detecter_theme_systeme():
    if platform.system() == "Windows":
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key_path = r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize'
            key = winreg.OpenKey(registry, key_path)
            apps_use_light_theme, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
            return "clair" if apps_use_light_theme == 1 else "sombre"
        except Exception:
            return "clair"
    return "clair"

# --- Page de questionnaire ---
class PageQuestionnaire(QWidget):
    questionnaire_valide = pyqtSignal(dict)
    
    def __init__(self, switch_callback):
        super().__init__()
        self.switch_callback = switch_callback

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(15)

        title = QLabel("Création d'un nouveau magasin")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(title)

        self.projet_input = self._add_labeled_input("Nom du projet :", "Saisissez le nom du projet", form_layout)
        self.auteur_input = self._add_labeled_input("Votre nom (Gérant) :", "Saisissez votre nom", form_layout) # Label updated
        self.date_input = self._add_date_input("Date de création :", form_layout) # Modified to use helper

        self.nom_magasin_input = self._add_labeled_input("Nom du magasin :", "Nom du magasin", form_layout)
        self.adresse_magasin_input = self._add_labeled_input("Adresse du magasin :", "Adresse complète", form_layout)

        btn_valider = QPushButton("Valider")
        btn_valider.clicked.connect(self.verifier_et_passer)
        form_layout.addWidget(btn_valider)

        outer_layout = QVBoxLayout()
        outer_layout.addStretch()
        outer_layout.addLayout(form_layout)
        outer_layout.addStretch()
        self.setLayout(outer_layout)

        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit, QDateEdit {
                border: 1px solid;
                border-radius: 5px;
                margin-bottom: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005999;
            }
        """)

    def _add_labeled_input(self, label_text, placeholder, layout):
        layout.addWidget(QLabel(label_text))
        line = QLineEdit()
        line.setPlaceholderText(placeholder)
        layout.addWidget(line)
        return line

    def _add_date_input(self, label_text, layout):
        layout.addWidget(QLabel(label_text))
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        layout.addWidget(date_edit)
        return date_edit

    def verifier_et_passer(self):
        if not all([
            self.projet_input.text().strip(),
            self.auteur_input.text().strip(),
            self.nom_magasin_input.text().strip(),
            self.adresse_magasin_input.text().strip()
        ]):
            QMessageBox.warning(self, "Champs requis", "Veuillez remplir tous les champs.")
            return
        self.questionnaire_valide.emit(self.get_questionnaire_data())
        self.switch_callback()

    def get_questionnaire_data(self):
        """Returns the data entered in the questionnaire."""
        return {
            "nom_projet": self.projet_input.text().strip(),
            "auteur": self.auteur_input.text().strip(),
            "date_creation": self.date_input.date().toString(Qt.DateFormat.ISODate),
            "nom_magasin": self.nom_magasin_input.text().strip(),
            "adresse_magasin": self.adresse_magasin_input.text().strip()
        }


# --- Choisir les produits disponibles dans le magasin ---
class ChoisirProduits(QWidget):
    selection_validee = pyqtSignal(dict)

    def __init__(self, fichier_produits='liste_produits.json'):
        super().__init__()
        self.setWindowTitle("Choisir les produits disponibles")
        self.setGeometry(100, 100, 600, 500)

        self.fichier_produits = fichier_produits
        self.produits_par_categorie = {}
        self.categories = []
        self.page_courante = 0
        self.categories_par_page = 3
        self.listes_categorie = {}
        self.selections_globales = {}

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        titre = QLabel("Sélectionnez les produits disponibles :")
        titre.setObjectName("titrePrincipal")
        self.layout.addWidget(titre)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)

        self.container = QWidget()
        self.scroll.setWidget(self.container)
        self.container_layout = QHBoxLayout()
        self.container.setLayout(self.container_layout)

        nav_layout = QHBoxLayout()
        self.btn_precedent = QPushButton("Page Précédente")
        self.btn_precedent.clicked.connect(self.page_precedente)
        nav_layout.addWidget(self.btn_precedent)
        self.btn_suivant = QPushButton("Page Suivante")
        self.btn_suivant.clicked.connect(self.page_suivante)
        nav_layout.addWidget(self.btn_suivant)
        self.layout.addLayout(nav_layout)

        self.btn_valider = QPushButton("Valider la sélection")
        self.btn_valider.clicked.connect(self.valider_selection)
        self.layout.addWidget(self.btn_valider)

        self.charger_produits()

    def charger_produits(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, self.fichier_produits)

            with open(file_path, 'r', encoding='utf-8') as f:
                self.produits_par_categorie = json.load(f)
        except FileNotFoundError:
            QMessageBox.critical(self, "Erreur", f"Le fichier '{self.fichier_produits}' n'a pas été trouvé. Veuillez vous assurer qu'il est dans le même répertoire que l'application.")
            self.produits_par_categorie = {}
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Erreur", f"Erreur de lecture du fichier '{self.fichier_produits}'. Assurez-vous qu'il s'agit d'un fichier JSON valide.")
            self.produits_par_categorie = {}
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger la liste des produits:\n{e}")
            self.produits_par_categorie = {}

        for categorie, produits in self.produits_par_categorie.items():
            for produit in produits:
                self.selections_globales[produit] = False

        self.categories = list(self.produits_par_categorie.keys())
        self.page_courante = 0
        self.afficher_page()

        self.setStyleSheet("""
            QLabel#titrePrincipal {
                font-size: 16px;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
            }

            QLabel#categorieLabel {
                font-weight: bold;
                font-size: 13px;
            }

            QListWidget {
                border: 1px solid gray;
                border-radius: 5px;
                padding: 5px;
            }

            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #005999;
            }
        """)

    def _sauvegarder_selections_courantes(self):
        for categorie, liste_widget in self.listes_categorie.items():
            for i in range(liste_widget.count()):
                item = liste_widget.item(i)
                if item.flags() & Qt.ItemFlag.ItemIsSelectable:
                    self.selections_globales[item.text()] = item.isSelected()

    def afficher_page(self):
        self._sauvegarder_selections_courantes()

        for i in reversed(range(self.container_layout.count())):
            layout_or_widget = self.container_layout.itemAt(i)
            if layout_or_widget is not None:
                widget = layout_or_widget.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    child_layout = layout_or_widget.layout()
                    if child_layout is not None:
                        self._clear_layout(child_layout)
                        self.container_layout.removeItem(child_layout)
                    else:
                        self.container_layout.removeItem(layout_or_widget)

        self.listes_categorie = {}

        start = self.page_courante * self.categories_par_page
        end = start + self.categories_par_page
        categories_a_afficher = self.categories[start:end]

        for categorie in categories_a_afficher:
            produits = self.produits_par_categorie[categorie]
            layout_categorie = QVBoxLayout()

            label = QLabel(categorie)
            label.setObjectName("categorieLabel")
            layout_categorie.addWidget(label)

            liste_widget = QListWidget()
            liste_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
            for produit in produits:
                item = QListWidgetItem(produit)
                if self.selections_globales.get(produit, False):
                    item.setSelected(True)
                liste_widget.addItem(item)
            layout_categorie.addWidget(liste_widget)

            self.container_layout.addLayout(layout_categorie)
            self.listes_categorie[categorie] = liste_widget

        self.btn_precedent.setEnabled(self.page_courante > 0)
        self.btn_suivant.setEnabled(end < len(self.categories))

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self._clear_layout(child_layout)

    def page_precedente(self):
        self._sauvegarder_selections_courantes()
        if self.page_courante > 0:
            self.page_courante -= 1
            self.afficher_page()

    def page_suivante(self):
        self._sauvegarder_selections_courantes()
        if (self.page_courante + 1) * self.categories_par_page < len(self.categories):
            self.page_courante += 1
            self.afficher_page()

    def valider_selection(self):
        self._sauvegarder_selections_courantes()

        selection_finale = {}
        total_selectionnes = 0

        for produit, selected in self.selections_globales.items():
            if selected:
                for categorie, produits_liste in self.produits_par_categorie.items():
                    if produit in produits_liste:
                        if categorie not in selection_finale:
                            selection_finale[categorie] = []
                        selection_finale[categorie].append(produit)
                        total_selectionnes += 1
                        break

        if total_selectionnes < 20:
            QMessageBox.warning(
                self,
                "Sélection insuffisante",
                f"Veuillez choisir au moins 20 produits (actuellement : {total_selectionnes})."
            )
            return

        self.selection_validee.emit(selection_finale)

class Image(QGraphicsView):
    produit_place_signal = pyqtSignal(str, QPointF)

    CELL_SIZE = 51

    def __init__(self, chemin: str):
        super().__init__()

        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._pixmap_item = QGraphicsPixmapItem()
        self._scene.addItem(self._pixmap_item)

        self._grid_cells = []
        self._product_text_items = {}
        self._product_positions_history = [] # For undo/redo
        self._history_index = -1 # For undo/redo

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
            self._scene.addWidget(label)
        else:
            self.setPixmap(pixmap)

    def setPixmap(self, pixmap: QPixmap):
        self._zoom = 0
        self._pixmap_item.setPixmap(pixmap)
        self._scene.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._empty = False
        self._draw_grid_overlay()
        self._product_positions_history = []
        self._history_index = -1

    def _draw_grid_overlay(self):
        for cell in self._grid_cells:
            self._scene.removeItem(cell)
        self._grid_cells.clear()

        # Keep existing product text items, only clear the grid
        # for product_item in self._product_text_items.values():
        #     self._scene.removeItem(product_item)
        # self._product_text_items.clear()


        image_width = self._pixmap_item.pixmap().width()
        image_height = self._pixmap_item.pixmap().height()

        grid_color_border = QColor(255, 0, 0, 100)
        grid_pen = QPen(grid_color_border)
        grid_pen.setWidth(2)

        for y in range(0, image_height, self.CELL_SIZE):
            for x in range(0, image_width, self.CELL_SIZE):
                rect_item = QGraphicsRectItem(x, y, self.CELL_SIZE, self.CELL_SIZE)
                rect_item.setPen(grid_pen)
                self._scene.addItem(rect_item)
                self._grid_cells.append(rect_item)
                rect_item.setZValue(1)

        self._pixmap_item.setZValue(0)

    def place_product_on_map(self, product_name: str, x: float, y: float, record_history=True):
        if product_name in self._product_text_items:
            self._scene.removeItem(self._product_text_items[product_name])
            del self._product_text_items[product_name]

        text_item = QGraphicsTextItem(product_name)
        text_item.setDefaultTextColor(QColor("red"))
        text_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        text_item.setPos(x - text_item.boundingRect().width() / 2,
                         y - text_item.boundingRect().height() / 2)

        text_item.setZValue(2)
        self._scene.addItem(text_item)
        self._product_text_items[product_name] = text_item

        if record_history:
            # Clear redo history
            del self._product_positions_history[self._history_index + 1:]
            self._product_positions_history.append((product_name, QPointF(x, y)))
            self._history_index += 1

    def remove_product_from_map(self, product_name: str):
        if product_name in self._product_text_items:
            self._scene.removeItem(self._product_text_items[product_name])
            del self._product_text_items[product_name]

    def undo_last_action(self):
        if self._history_index >= 0:
            last_action = self._product_positions_history[self._history_index]
            product_name_to_remove = last_action[0]
            self.remove_product_from_map(product_name_to_remove)
            self._history_index -= 1
            # Re-draw the remaining products from history to reflect the state
            self._redraw_products_from_history()
            return True
        return False

    def redo_last_action(self):
        if self._history_index + 1 < len(self._product_positions_history):
            self._history_index += 1
            action_to_redo = self._product_positions_history[self._history_index]
            self.place_product_on_map(action_to_redo[0], action_to_redo[1].x(), action_to_redo[1].y(), record_history=False)
            return True
        return False

    def _redraw_products_from_history(self):
        # Clear all current products on map
        for product_item in list(self._product_text_items.values()):
            self._scene.removeItem(product_item)
        self._product_text_items.clear()

        # Redraw products up to current history index
        for i in range(self._history_index + 1):
            product_name, position = self._product_positions_history[i]
            self.place_product_on_map(product_name, position.x(), position.y(), record_history=False)


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
            product_name = event.mimeData().text()
            scene_pos = self.mapToScene(event.position().toPoint())

            # Calculate the top-left corner of the grid cell
            grid_x = (int(scene_pos.x()) // self.CELL_SIZE) * self.CELL_SIZE
            grid_y = (int(scene_pos.y()) // self.CELL_SIZE) * self.CELL_SIZE

            # Calculate the center of that specific grid cell
            center_x = grid_x + self.CELL_SIZE / 2
            center_y = grid_y + self.CELL_SIZE / 2

            self.place_product_on_map(product_name, center_x, center_y, record_history=True)

            event.acceptProposedAction()
            self.produit_place_signal.emit(product_name, QPointF(center_x, center_y))
        else:
            event.ignore()

# Nouvelle classe personnalisée pour le QListWidget
class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True) # Active le glisser-déposer depuis cette liste
        self.setDragDropMode(QListWidget.DragDropMode.DragOnly) # Permet seulement de glisser, pas de déposer sur la liste
        self.setDefaultDropAction(Qt.DropAction.MoveAction) # Action par défaut est le déplacement

    def startDrag(self, supportedActions):
        # Récupère l'élément qui a été cliqué pour commencer le glisser
        item = self.currentItem()
        if item is None:
            return # Aucun élément à glisser

        # S'assurer que ce n'est pas un titre de catégorie ou un élément non glissable
        if not (item.flags() & Qt.ItemFlag.ItemIsDragEnabled):
            return

        mime_data = QMimeData()
        mime_data.setText(item.text()) # C'est la ligne clé : s'assurer que le texte est dans le QMimeData

        drag = QDrag(self)
        drag.setMimeData(mime_data)

        # Exécute l'opération de glisser
        drag.exec(supportedActions)

class FenetreAppli(QMainWindow):
    def __init__(self, chemin: str = None, produits_selectionnes: dict = None, questionnaire_data: dict = None):
        super().__init__()
        self.__chemin = chemin
        self.produits_selectionnes = produits_selectionnes if produits_selectionnes is not None else {}
        self.positions_produits = {} # This will store the final saved positions
        self.questionnaire_data = questionnaire_data if questionnaire_data is not None else {}

        self.setWindowTitle("Gestionnaire de Magasin (Gérant)")
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen_geometry)

        # --- Top Bar for Store Info ---
        self.top_bar_widget = QWidget()
        self.top_bar_layout = QHBoxLayout() # This will hold the QVBox and a stretch
        self.top_bar_widget.setLayout(self.top_bar_layout)
        self.top_bar_widget.setFixedHeight(90) # Increased height to accommodate more info and padding
        self.top_bar_widget.setStyleSheet("background-color: #f0f0f0;") # Removed border-bottom

        # Inner QVBoxLayout for stacked information
        self.info_stack_layout = QVBoxLayout()
        self.info_stack_layout.setContentsMargins(0, 0, 0, 0) # Removed padding as QLabel.setAlignment handles centering
        self.info_stack_layout.setSpacing(2) # Spacing between labels

        self.store_name_label = QLabel("Magasin : N/A")
        self.store_name_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #005999;") # Stronger style
        self.store_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # Center alignment
        self.info_stack_layout.addWidget(self.store_name_label)

        self.gerant_name_label = QLabel("Gérant : N/A")
        self.gerant_name_label.setStyleSheet("font-size: 14px; color: #333;")
        self.gerant_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # Center alignment
        self.info_stack_layout.addWidget(self.gerant_name_label)

        self.store_address_label = QLabel("Adresse : N/A")
        self.store_address_label.setStyleSheet("font-size: 14px; color: #333;")
        self.store_address_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # Center alignment
        self.info_stack_layout.addWidget(self.store_address_label)

        # Use stretches to center the info_stack_layout within the top_bar_layout
        self.top_bar_layout.addStretch(1) # Left stretch
        self.top_bar_layout.addLayout(self.info_stack_layout) # Add the stacked info
        self.top_bar_layout.addStretch(1) # Right stretch
        # --- End Top Bar ---

        self.main_content_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_content_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.main_layout.addWidget(self.top_bar_widget) # Add the top bar
        self.image_viewer = Image(self.__chemin)
        self.main_layout.addWidget(self.image_viewer) # Add the image viewer below the top bar
        self.setCentralWidget(self.main_content_widget) # Set the main content widget as central

        self.image_viewer.produit_place_signal.connect(self.enregistrer_position_produit)

        self.dock = QDockWidget('Produits à placer')
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        self.dock.setMaximumWidth(400)

        self.liste_produits_dock = DraggableListWidget()
        self.dock.setWidget(self.liste_produits_dock)

        self.afficher_produits_dans_dock()

        self.barre_etat = QStatusBar()
        self.setStatusBar(self.barre_etat)
        self.barre_etat.showMessage("Application démarrée. Choisissez un plan et placez les produits.", 2000)

        menu_bar = self.menuBar()
        menu_fichier = menu_bar.addMenu('&Fichier')
        menu_edition = menu_bar.addMenu('&Edition')
        menu_affichage = menu_bar.addMenu('&Affichage')

        menu_fichier.addAction('Nouveau plan', self.nouveau)
        menu_fichier.addAction('Ouvrir un plan', self.ouvrir)
        menu_fichier.addAction('Enregistrer les positions temporaires', self.enregistrer_positions) # Renamed for clarity
        menu_fichier.addAction('Enregistrer le plan final', self.enregistrer_plan_final) # New action
        menu_fichier.addSeparator()
        menu_fichier.addAction('Quitter', QCoreApplication.instance().quit) # Use QCoreApplication.instance().quit

        # New actions for "Edition" menu (Undo/Redo)
        self.action_undo = menu_edition.addAction('Annuler', self.undo_action)
        self.action_redo = menu_edition.addAction('Rétablir', self.redo_action)
        self.action_undo.setShortcut('Ctrl+Z')
        self.action_redo.setShortcut('Ctrl+Y')
        self._update_undo_redo_actions_state() # Initial state

        # New action for "Affichage" menu (Toggle Product List Dock)
        self.action_toggle_dock = menu_affichage.addAction('Afficher/Masquer la liste des produits', self.toggle_product_list_dock)
        self.action_toggle_dock.setCheckable(True)
        self.action_toggle_dock.setChecked(True) # Dock is visible by default

        self.showMaximized()

        self._update_store_info_display() # Update all store info on init

    def _update_store_info_display(self):
        """Updates all the QLabels in the top bar with data from questionnaire_data."""
        nom_magasin = self.questionnaire_data.get("nom_magasin", "N/A")
        auteur = self.questionnaire_data.get("auteur", "N/A")
        adresse_magasin = self.questionnaire_data.get("adresse_magasin", "N/A")

        self.store_name_label.setText(f"Magasin : {nom_magasin}")
        self.gerant_name_label.setText(f"Gérant : {auteur}")
        self.store_address_label.setText(f"Adresse : {adresse_magasin}")

    def _update_undo_redo_actions_state(self):
        # Enable/disable undo/redo based on history state
        self.action_undo.setEnabled(self.image_viewer._history_index >= 0)
        self.action_redo.setEnabled(self.image_viewer._history_index + 1 < len(self.image_viewer._product_positions_history))


    def afficher_produits_dans_dock(self):
        self.liste_produits_dock.clear()
        if not self.produits_selectionnes:
            item = QListWidgetItem("Aucun produit sélectionné dans le questionnaire.")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled & ~Qt.ItemFlag.ItemIsDragEnabled & ~Qt.ItemFlag.ItemIsSelectable)
            self.liste_produits_dock.addItem(item)
            return

        for categorie, produits in self.produits_selectionnes.items():
            category_item = QListWidgetItem(f"--- {categorie} ---")
            category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsDragEnabled & ~Qt.ItemFlag.ItemIsSelectable)
            category_item.setForeground(QBrush(QColor("blue")))
            self.liste_produits_dock.addItem(category_item)

            for produit in produits:
                item = QListWidgetItem(produit)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsSelectable)
                self.liste_produits_dock.addItem(item)

    def enregistrer_position_produit(self, product_name: str, position: QPointF):
        # Update the dictionary storing final positions (this is independent of undo/redo history)
        self.positions_produits[product_name] = {'x': position.x(), 'y': position.y()}
        self.barre_etat.showMessage(f"Produit '{product_name}' placé à ({position.x():.0f}, {position.y():.0f})", 3000)
        self._update_undo_redo_actions_state()

    def undo_action(self):
        if self.image_viewer.undo_last_action():
            # Update self.positions_produits based on the current history state
            self.positions_produits.clear()
            for product_name, pos in self.image_viewer._product_positions_history[:self.image_viewer._history_index + 1]:
                self.positions_produits[product_name] = {'x': pos.x(), 'y': pos.y()}
            self.barre_etat.showMessage("Action annulée.", 2000)
        else:
            self.barre_etat.showMessage("Aucune action à annuler.", 2000)
        self._update_undo_redo_actions_state()

    def redo_action(self):
        if self.image_viewer.redo_last_action():
            # Update self.positions_produits based on the current history state
            product_name, pos = self.image_viewer._product_positions_history[self.image_viewer._history_index]
            self.positions_produits[product_name] = {'x': pos.x(), 'y': pos.y()}
            self.barre_etat.showMessage("Action rétablie.", 2000)
        else:
            self.barre_etat.showMessage("Aucune action à rétablir.", 2000)
        self._update_undo_redo_actions_state()

    def toggle_product_list_dock(self):
        if self.dock.isVisible():
            self.dock.hide()
            self.action_toggle_dock.setChecked(False)
            self.barre_etat.showMessage("Liste des produits masquée.", 2000)
        else:
            self.dock.show()
            self.action_toggle_dock.setChecked(True)
            self.barre_etat.showMessage("Liste des produits affichée.", 2000)


    def enregistrer_positions(self):
        if not self.positions_produits:
            QMessageBox.information(self, "Enregistrer les positions temporaires", "Aucun produit n'a été placé pour être enregistré temporairement.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer les positions temporaires des produits",
                                                 "positions_temp.json",
                                                 "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    serializable_positions = {
                        name: {'x': pos['x'], 'y': pos['y']}
                        for name, pos in self.positions_produits.items()
                    }
                    json.dump(serializable_positions, f, indent=4, ensure_ascii=False)
                self.barre_etat.showMessage(f"Positions temporaires enregistrées dans {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'enregistrement", f"Impossible d'enregistrer les positions temporaires:\n{e}")

    def enregistrer_plan_final(self):
        """
        Saves the complete project data: questionnaire, selected products,
        plan image path, and final product positions.
        """
        if not self.__chemin:
            QMessageBox.warning(self, "Enregistrer le plan final", "Aucun plan de magasin n'est chargé.")
            return

        if not self.produits_selectionnes:
            QMessageBox.warning(self, "Enregistrer le plan final", "Aucun produit n'a été sélectionné pour le magasin.")
            return

        if not self.positions_produits:
            QMessageBox.warning(self, "Enregistrer le plan final", "Aucun produit n'a été placé sur le plan.")
            return

        project_data = {
            "questionnaire_info": self.questionnaire_data,
            "chemin_image_plan": self.__chemin,
            "produits_selectionnes": self.produits_selectionnes,
            "positions_produits_finales": {
                name: {'x': pos['x'], 'y': pos['y']}
                for name, pos in self.positions_produits.items()
            }
        }

        file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer le plan final du magasin",
                                                 "mon_magasin_final.json",
                                                 "Fichiers Magasin (*.json)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, indent=4, ensure_ascii=False)
                self.barre_etat.showMessage(f"Plan final enregistré dans {file_path}", 5000)
                QMessageBox.information(self, "Enregistrement réussi", f"Le plan final du magasin a été enregistré dans :\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'enregistrement", f"Impossible d'enregistrer le plan final:\n{e}")


    def nouveau(self):
        self.barre_etat.showMessage('Création d\'un nouveau plan...', 2000)
        boite = QFileDialog()
        chemin, validation = boite.getOpenFileName(self, "Sélectionner un nouveau plan de magasin",
                                                 directory = os.path.join(sys.path[0]),
                                                 filter="Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if validation:
            self.__chemin = chemin
            self.image_viewer.setPixmap(QPixmap(self.__chemin))
            self.positions_produits.clear()
            self.image_viewer._product_positions_history = [] # Clear history on new plan
            self.image_viewer._history_index = -1
            self._update_undo_redo_actions_state()
            self.barre_etat.showMessage('Nouveau plan chargé. Vous pouvez placer des produits.', 2000)
        else:
            self.barre_etat.showMessage('Création de nouveau plan annulée.', 2000)

    def ouvrir(self):
        self.barre_etat.showMessage('Ouvrir un plan existant....', 2000)
        file_path, _ = QFileDialog.getOpenFileName(self, "Ouvrir un plan de magasin enregistré",
                                                 "", # Default directory
                                                 "Fichiers Magasin (*.json)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)

                chemin_image = project_data.get("chemin_image_plan")
                if not os.path.exists(chemin_image):
                    QMessageBox.warning(self, "Erreur", f"L'image du plan '{chemin_image}' n'a pas été trouvée. Veuillez la replacer ou choisir un nouveau plan.")
                    return

                self.__chemin = chemin_image
                self.image_viewer.setPixmap(QPixmap(self.__chemin))

                self.questionnaire_data = project_data.get("questionnaire_info", {})
                self._update_store_info_display() # Update all store info when loading a project

                self.produits_selectionnes = project_data.get("produits_selectionnes", {})
                self.afficher_produits_dans_dock()

                self.positions_produits.clear()
                self.image_viewer._product_positions_history = [] # Clear history before loading new
                self.image_viewer._history_index = -1
                
                # Clear existing product graphics before loading new ones
                for item_graphic in list(self.image_viewer._product_text_items.values()):
                    self.image_viewer._scene.removeItem(item_graphic)
                self.image_viewer._product_text_items.clear()

                loaded_positions = project_data.get("positions_produits_finales", {})
                for product_name, pos_data in loaded_positions.items():
                    x = pos_data.get('x')
                    y = pos_data.get('y')
                    if x is not None and y is not None:
                        # Place product on map and record to history
                        self.image_viewer.place_product_on_map(product_name, x, y, record_history=True)
                        # Also update the main positions_produits dictionary
                        self.positions_produits[product_name] = {'x': x, 'y': y}

                self.barre_etat.showMessage(f"Plan chargé: {file_path}", 3000)
                self._update_undo_redo_actions_state()


            except json.JSONDecodeError:
                QMessageBox.critical(self, "Erreur d'ouverture", "Le fichier sélectionné n'est pas un fichier JSON valide.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'ouverture", f"Impossible d'ouvrir le plan:\n{e}")
        else:
            self.barre_etat.showMessage('Ouverture de plan annulée.', 2000)


# --- Gestionnaire de navigation entre pages ---
class AppMultiPages(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.page_questionnaire = PageQuestionnaire(self.aller_a_choisir_produits)
        self.controller = ControlleurGerant(self.page_questionnaire)
        self.addWidget(self.page_questionnaire)  # index 0

        self.choisir_produits = ChoisirProduits()
        self.choisir_produits.selection_validee.connect(self.aller_a_fenetre_appli)
        self.addWidget(self.choisir_produits) # index 1

        self.fenetre_appli = None

        self.setCurrentIndex(0)

    def aller_a_choisir_produits(self):
        self.setCurrentIndex(1)
        self.choisir_produits.charger_produits()

    def aller_a_fenetre_appli(self, produits_selectionnes: dict):
        chemin_image = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Quadrillage_Final.jpg')
        questionnaire_data = self.page_questionnaire.get_questionnaire_data() # Get data from questionnaire

        if self.fenetre_appli is None:
            self.fenetre_appli = FenetreAppli(
                chemin=chemin_image,
                produits_selectionnes=produits_selectionnes,
                questionnaire_data=questionnaire_data # Pass questionnaire data
            )
            self.addWidget(self.fenetre_appli)  # index 2
        else:
            self.fenetre_appli.produits_selectionnes = produits_selectionnes
            self.fenetre_appli.questionnaire_data = questionnaire_data # Update data
            self.fenetre_appli.afficher_produits_dans_dock()
            self.fenetre_appli.positions_produits.clear()
            self.fenetre_appli.image_viewer._product_positions_history = [] # Clear history on new selection
            self.fenetre_appli.image_viewer._history_index = -1
            for item in list(self.fenetre_appli.image_viewer._product_text_items.values()):
                self.fenetre_appli.image_viewer._scene.removeItem(item)
            self.fenetre_appli.image_viewer._product_text_items.clear()
            self.fenetre_appli.image_viewer._draw_grid_overlay() # Redraw grid and clear product items
            self.fenetre_appli._update_store_info_display() # Update all store info display on existing window
            self.fenetre_appli._update_undo_redo_actions_state()


        self.setCurrentIndex(2)

# --- Lancement de l'application ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    multi_pages = AppMultiPages()
    multi_pages.setWindowTitle("Application Gérant de Magasin")
    multi_pages.resize(1280, 720)
    multi_pages.show()
    sys.exit(app.exec())