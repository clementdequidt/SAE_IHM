# VUE_CLIENT

import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QStatusBar,
    QLabel, QTextEdit, QFileDialog, QDockWidget, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QWidget,
    QListWidget, QPushButton, QHBoxLayout, QMessageBox, QListWidgetItem
)
from PyQt6.QtGui import QIcon, QAction, QPixmap, QMouseEvent, QWheelEvent, QPainter, QFont, QColor
from PyQt6.QtCore import Qt, QPointF, QRectF, QCoreApplication


# --- Image Widget (QGraphicsView for displaying map and products) ---
class Image(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._pixmap_item = QGraphicsPixmapItem()
        self._scene.addItem(self._pixmap_item)

        self._product_text_items = {} # To store QGraphicsTextItem for each product

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    def setPixmap(self, pixmap: QPixmap):
        """Sets the background pixmap for the scene."""
        self._zoom = 0
        self._pixmap_item.setPixmap(pixmap)
        self._scene.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._empty = False
        # Ensure pixmap is at the bottom Z-value
        self._pixmap_item.setZValue(0)

        # Clear any existing product labels when a new pixmap is set
        self.clear_all_product_labels()

    def place_product_on_map(self, product_name: str, x: float, y: float):
        """
        Places a product label on the map at the given scene coordinates.
        Removes existing label for the same product if present.
        """
        # Remove existing label for this product if it's already on the map
        if product_name in self._product_text_items:
            self._scene.removeItem(self._product_text_items[product_name])
            del self._product_text_items[product_name]

        # Create new text item for the product
        text_item = self._scene.addText(product_name)
        text_item.setDefaultTextColor(QColor("red")) # Products will be red for clients
        text_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        # Position the text item so its center is at (x, y)
        text_item.setPos(x - text_item.boundingRect().width() / 2,
                         y - text_item.boundingRect().height() / 2)

        text_item.setZValue(1) # Ensure product labels are above the map
        self._product_text_items[product_name] = text_item

    def clear_all_product_labels(self):
        """Removes all product labels currently displayed on the map."""
        for item in list(self._product_text_items.values()):
            self._scene.removeItem(item)
        self._product_text_items.clear()


    def wheelEvent(self, event: QWheelEvent):
        """Handles mouse wheel events for zooming."""
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

        # Prevent excessive zooming
        if self._zoom < -10:
            self._zoom = -10
            return
        if self._zoom > 30:
            self._zoom = 30
            return

        self.scale(zoom_factor, zoom_factor)


# --- Main Application Window ---
class FenetreAppli(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Application Client de Magasin")
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen_geometry)

        # --- Data holders ---
        self.questionnaire_data = {}
        self.products_available_in_store = {} # Category -> [product names]
        self.product_positions_on_map = {} # Product name -> {'x': float, 'y': float}

        # --- Top Bar for Store Info ---
        # Create a QToolBar first
        self.top_bar_toolbar = QToolBar("Informations du Magasin")
        self.top_bar_toolbar.setMovable(False) # Make it non-movable
        self.top_bar_toolbar.toggleViewAction().setVisible(False) # Hide the toggle view action
        
        self.top_bar_widget = QWidget()
        self.top_bar_layout = QHBoxLayout(self.top_bar_widget) # Set layout directly to the widget
        self.top_bar_widget.setFixedHeight(90)
        self.top_bar_widget.setStyleSheet("background-color: #f0f0f0;")

        self.info_stack_layout = QVBoxLayout()
        self.info_stack_layout.setContentsMargins(0, 0, 0, 0)
        self.info_stack_layout.setSpacing(2)

        self.store_name_label = QLabel("Magasin : Aucun plan chargé")
        self.store_name_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #005999;")
        self.store_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_stack_layout.addWidget(self.store_name_label)

        self.gerant_name_label = QLabel("Gérant : N/A")
        self.gerant_name_label.setStyleSheet("font-size: 14px; color: #333;")
        self.gerant_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_stack_layout.addWidget(self.gerant_name_label)

        self.store_address_label = QLabel("Adresse : N/A")
        self.store_address_label.setStyleSheet("font-size: 14px; color: #333;")
        self.store_address_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_stack_layout.addWidget(self.store_address_label)

        self.top_bar_layout.addStretch(1)
        self.top_bar_layout.addLayout(self.info_stack_layout)
        self.top_bar_layout.addStretch(1)
        
        # Add the widget to the toolbar
        self.top_bar_toolbar.addWidget(self.top_bar_widget)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.top_bar_toolbar) # Add the QToolBar to the QMainWindow

        # --- Main content: Image Viewer ---
        self.image_viewer = Image()
        self.setCentralWidget(self.image_viewer)

        # --- Docks for Product List and Shopping List ---
        self.available_products_dock = QDockWidget('Produits Disponibles')
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.available_products_dock)
        self.available_products_dock.setMaximumWidth(400)

        self.available_products_list_widget = QListWidget()
        self.available_products_list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        # Shopping list widget and controls
        shopping_list_container = QWidget()
        shopping_list_layout = QVBoxLayout(shopping_list_container)
        
        # Label for Available Products
        available_label = QLabel("Produits disponibles dans le magasin :")
        available_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        shopping_list_layout.addWidget(available_label)
        shopping_list_layout.addWidget(self.available_products_list_widget)

        add_to_list_btn = QPushButton("Ajouter à la liste de courses")
        add_to_list_btn.clicked.connect(self.add_selected_to_shopping_list)
        shopping_list_layout.addWidget(add_to_list_btn)

        shopping_list_label = QLabel("Ma liste de courses :")
        shopping_list_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px; margin-bottom: 5px;")
        shopping_list_layout.addWidget(shopping_list_label)

        self.shopping_list_widget = QListWidget()
        self.shopping_list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        shopping_list_layout.addWidget(self.shopping_list_widget)

        shopping_list_buttons_layout = QHBoxLayout()
        remove_from_list_btn = QPushButton("Retirer")
        remove_from_list_btn.clicked.connect(self.remove_selected_from_shopping_list)
        shopping_list_buttons_layout.addWidget(remove_from_list_btn)

        clear_list_btn = QPushButton("Tout effacer")
        clear_list_btn.clicked.connect(self.clear_shopping_list)
        shopping_list_buttons_layout.addWidget(clear_list_btn)

        save_list_btn = QPushButton("Enregistrer la liste")
        save_list_btn.clicked.connect(self.save_shopping_list)
        shopping_list_buttons_layout.addWidget(save_list_btn)
        
        shopping_list_layout.addLayout(shopping_list_buttons_layout)

        self.available_products_dock.setWidget(shopping_list_container)


        # --- Status Bar ---
        self.barre_etat = QStatusBar()
        self.setStatusBar(self.barre_etat)
        self.barre_etat.showMessage("Veuillez ouvrir un plan de magasin...", 2000)

        # --- Menu Bar ---
        menu_bar = self.menuBar()

        menu_fichier = menu_bar.addMenu('&Fichier')
        menu_affichage = menu_bar.addMenu('&Affichage')

        menu_fichier.addAction('Ouvrir un plan de magasin', self.ouvrir_plan_magasin)
        menu_fichier.addSeparator()
        menu_fichier.addAction('Quitter', QCoreApplication.instance().quit)

        # Action to toggle product list dock visibility
        self.action_toggle_dock = menu_affichage.addAction('Afficher/Masquer le panneau des produits', self.toggle_product_list_dock)
        self.action_toggle_dock.setCheckable(True)
        self.action_toggle_dock.setChecked(True) # Dock is visible by default


        self.showMaximized()
        self._apply_styles()

    def _apply_styles(self):
        """Applies consistent styling to various widgets."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f8f8;
            }
            QDockWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QDockWidget::title {
                background: #e0e0e0;
                padding: 5px;
                border-bottom: 1px solid #ccc;
            }
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 3px;
            }
            QListWidget::item:selected {
                background-color: #a0c0e0;
                color: black;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                margin: 5px 0;
            }
            QPushButton:hover {
                background-color: #005999;
            }
            QLabel {
                color: #333;
            }
        """)


    def _update_store_info_display(self):
        """Updates the QLabels in the top bar with loaded store data."""
        nom_magasin = self.questionnaire_data.get("nom_magasin", "Aucun plan chargé")
        auteur = self.questionnaire_data.get("auteur", "N/A")
        adresse_magasin = self.questionnaire_data.get("adresse_magasin", "N/A")

        self.store_name_label.setText(f"Magasin : {nom_magasin}")
        self.gerant_name_label.setText(f"Gérant : {auteur}")
        self.store_address_label.setText(f"Adresse : {adresse_magasin}")

    def display_available_products(self):
        """Populates the available products list widget."""
        self.available_products_list_widget.clear()
        if not self.products_available_in_store:
            item = QListWidgetItem("Aucun produit disponible dans ce magasin.")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled) # Make it non-selectable
            self.available_products_list_widget.addItem(item)
            return

        for category, products in self.products_available_in_store.items():
            category_item = QListWidgetItem(f"--- {category} ---")
            category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsSelectable) # Make category non-selectable
            category_item.setForeground(QColor("blue"))
            self.available_products_list_widget.addItem(category_item)

            for product in products:
                item = QListWidgetItem(product)
                self.available_products_list_widget.addItem(item)

    def add_selected_to_shopping_list(self):
        """Adds selected items from available products to the shopping list.
        Allows adding the same product multiple times."""
        selected_items = self.available_products_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Sélection vide", "Veuillez sélectionner au moins un produit à ajouter.")
            return

        for item in selected_items:
            product_name = item.text()
            # Avoid adding category headers
            if not product_name.startswith("---"):
                self.shopping_list_widget.addItem(QListWidgetItem(product_name))
        self.barre_etat.showMessage(f"Produits ajoutés à la liste de courses.", 2000)


    def remove_selected_from_shopping_list(self):
        """Removes selected items from the shopping list."""
        selected_items = self.shopping_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Sélection vide", "Veuillez sélectionner au moins un produit à retirer.")
            return

        for item in selected_items:
            row = self.shopping_list_widget.row(item)
            self.shopping_list_widget.takeItem(row)
        self.barre_etat.showMessage(f"Produits retirés de la liste de courses.", 2000)

    def clear_shopping_list(self):
        """Clears all items from the shopping list."""
        if self.shopping_list_widget.count() == 0:
            QMessageBox.information(self, "Liste vide", "La liste de courses est déjà vide.")
            return

        reply = QMessageBox.question(self, 'Effacer la liste',
                                     "Êtes-vous sûr de vouloir effacer toute la liste de courses?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.shopping_list_widget.clear()
            self.barre_etat.showMessage("Liste de courses effacée.", 2000)

    def save_shopping_list(self):
        """Saves the current shopping list to a text file."""
        if self.shopping_list_widget.count() == 0:
            QMessageBox.information(self, "Liste vide", "La liste de courses est vide et ne peut pas être enregistrée.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer la liste de courses",
                                                 "ma_liste_de_courses.txt",
                                                 "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for i in range(self.shopping_list_widget.count()):
                        f.write(self.shopping_list_widget.item(i).text() + '\n')
                self.barre_etat.showMessage(f"Liste de courses enregistrée dans {file_path}", 3000)
                QMessageBox.information(self, "Enregistrement réussi", f"Votre liste de courses a été enregistrée dans :\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'enregistrement", f"Impossible d'enregistrer la liste de courses:\n{e}")

    def toggle_product_list_dock(self):
        """Toggles the visibility of the product list dock."""
        if self.available_products_dock.isVisible():
            self.available_products_dock.hide()
            self.action_toggle_dock.setChecked(False)
            self.barre_etat.showMessage("Panneau des produits masqué.", 2000)
        else:
            self.available_products_dock.show()
            self.action_toggle_dock.setChecked(True)
            self.barre_etat.showMessage("Panneau des produits affiché.", 2000)

    def ouvrir_plan_magasin(self):
        """Opens a previously saved store plan JSON file."""
        self.barre_etat.showMessage('Ouverture d\'un plan de magasin...', 2000)
        file_path, _ = QFileDialog.getOpenFileName(self, "Ouvrir un plan de magasin enregistré",
                                                 "", # Default directory
                                                 "Fichiers Magasin (*.json)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)

                # Load store info
                self.questionnaire_data = project_data.get("questionnaire_info", {})
                self._update_store_info_display()

                # Load map image
                image_path = project_data.get("chemin_image_plan")
                if not os.path.exists(image_path):
                    QMessageBox.warning(self, "Erreur de fichier",
                                        f"L'image du plan '{image_path}' n'a pas été trouvée. "
                                        "Veuillez vérifier le chemin ou charger un autre plan.")
                    return

                self.image_viewer.setPixmap(QPixmap(image_path))

                # Load available products and display in dock
                self.products_available_in_store = project_data.get("produits_selectionnes", {})
                self.display_available_products()

                # Load and display product positions on the map
                self.product_positions_on_map = project_data.get("positions_produits_finales", {})
                self.image_viewer.clear_all_product_labels() # Clear existing before placing new
                for product_name, pos_data in self.product_positions_on_map.items():
                    x = pos_data.get('x')
                    y = pos_data.get('y')
                    if x is not None and y is not None:
                        self.image_viewer.place_product_on_map(product_name, x, y)
                
                # Clear existing shopping list for a new store
                self.shopping_list_widget.clear()

                self.barre_etat.showMessage(f"Plan de magasin chargé: {file_path}", 3000)

            except json.JSONDecodeError:
                QMessageBox.critical(self, "Erreur d'ouverture", "Le fichier sélectionné n'est pas un fichier JSON valide.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'ouverture", f"Impossible d'ouvrir le plan de magasin:\n{e}")
        else:
            self.barre_etat.showMessage('Ouverture de plan annulée.', 2000)


# --- Main application entry point ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetreAppli()
    fenetre.show()
    sys.exit(app.exec())