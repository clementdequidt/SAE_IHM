# MVC_VIEW.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QStatusBar,
    QLabel, QFileDialog, QDockWidget, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QWidget,
    QListWidget, QPushButton, QHBoxLayout, QMessageBox, QListWidgetItem
)
from PyQt6.QtGui import QPixmap, QWheelEvent, QPainter, QFont, QColor
from PyQt6.QtCore import Qt, QPointF, QRectF, QCoreApplication


# --- Image Widget (QGraphicsView for displaying map and products) ---
class ImageView(QGraphicsView):
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

    def set_map_pixmap(self, pixmap: QPixmap):
        """Sets the background pixmap for the scene."""
        self._zoom = 0
        self._pixmap_item.setPixmap(pixmap)
        self._scene.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._empty = False
        self._pixmap_item.setZValue(0) # Ensure pixmap is at the bottom Z-value

    def place_product_label(self, product_name: str, x: float, y: float):
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
class FenetreAppliView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application Client de Magasin")
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen_geometry)

        self._setup_ui()
        self._apply_styles()
        self.showMaximized()

    def _setup_ui(self):
        # --- Top Bar for Store Info ---
        self.top_bar_toolbar = QToolBar("Informations du Magasin")
        self.top_bar_toolbar.setMovable(False)
        self.top_bar_toolbar.toggleViewAction().setVisible(False)
        
        self.top_bar_widget = QWidget()
        self.top_bar_layout = QHBoxLayout(self.top_bar_widget)
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
        
        self.top_bar_toolbar.addWidget(self.top_bar_widget)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.top_bar_toolbar)

        # --- Main content: Image Viewer ---
        self.image_viewer = ImageView()
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
        
        available_label = QLabel("Produits disponibles dans le magasin :")
        available_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        shopping_list_layout.addWidget(available_label)
        shopping_list_layout.addWidget(self.available_products_list_widget)

        self.add_to_list_btn = QPushButton("Ajouter à la liste de courses")
        shopping_list_layout.addWidget(self.add_to_list_btn)

        shopping_list_label = QLabel("Ma liste de courses :")
        shopping_list_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px; margin-bottom: 5px;")
        shopping_list_layout.addWidget(shopping_list_label)

        self.shopping_list_widget = QListWidget()
        self.shopping_list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        shopping_list_layout.addWidget(self.shopping_list_widget)

        shopping_list_buttons_layout = QHBoxLayout()
        self.remove_from_list_btn = QPushButton("Retirer")
        shopping_list_buttons_layout.addWidget(self.remove_from_list_btn)

        self.clear_list_btn = QPushButton("Tout effacer")
        shopping_list_buttons_layout.addWidget(self.clear_list_btn)

        self.save_list_btn = QPushButton("Enregistrer la liste")
        shopping_list_buttons_layout.addWidget(self.save_list_btn)
        
        shopping_list_layout.addLayout(shopping_list_buttons_layout)

        self.available_products_dock.setWidget(shopping_list_container)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Veuillez ouvrir un plan de magasin...", 2000)

        # --- Menu Bar ---
        menu_bar = self.menuBar()

        menu_fichier = menu_bar.addMenu('&Fichier')
        menu_affichage = menu_bar.addMenu('&Affichage')

        self.open_plan_action = menu_fichier.addAction('Ouvrir un plan de magasin')
        menu_fichier.addSeparator()
        self.quit_action = menu_fichier.addAction('Quitter')

        self.action_toggle_dock = menu_affichage.addAction('Afficher/Masquer le panneau des produits')
        self.action_toggle_dock.setCheckable(True)
        self.action_toggle_dock.setChecked(True) # Dock is visible by default

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

    # --- Methods to update UI based on Model data ---
    def update_store_info(self, store_info: dict):
        """Updates the QLabels in the top bar with loaded store data."""
        self.store_name_label.setText(f"Magasin : {store_info.get('nom_magasin', 'Aucun plan chargé')}")
        self.gerant_name_label.setText(f"Gérant : {store_info.get('auteur', 'N/A')}")
        self.store_address_label.setText(f"Adresse : {store_info.get('adresse_magasin', 'N/A')}")

    def display_map(self, pixmap: QPixmap):
        """Displays the given pixmap on the image viewer."""
        self.image_viewer.set_map_pixmap(pixmap)

    def display_available_products(self, products_by_category: dict):
        """Populates the available products list widget."""
        self.available_products_list_widget.clear()
        if not products_by_category:
            item = QListWidgetItem("Aucun produit disponible dans ce magasin.")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled) # Make it non-selectable
            self.available_products_list_widget.addItem(item)
            return

        for category, products in products_by_category.items():
            category_item = QListWidgetItem(f"--- {category} ---")
            category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsSelectable) # Make category non-selectable
            category_item.setForeground(QColor("blue"))
            self.available_products_list_widget.addItem(category_item)

            for product in products:
                item = QListWidgetItem(product)
                self.available_products_list_widget.addItem(item)

    def display_product_positions_on_map(self, product_positions: dict):
        """Displays product labels on the map based on their positions."""
        self.image_viewer.clear_all_product_labels()
        for product_name, pos_data in product_positions.items():
            x = pos_data.get('x')
            y = pos_data.get('y')
            if x is not None and y is not None:
                self.image_viewer.place_product_label(product_name, x, y)

    def update_shopping_list_display(self, shopping_list: list[str]):
        """Updates the shopping list widget with the current list."""
        self.shopping_list_widget.clear()
        for product in shopping_list:
            self.shopping_list_widget.addItem(QListWidgetItem(product))

    def show_status_message(self, message: str, timeout: int = 2000):
        """Displays a message in the status bar."""
        self.status_bar.showMessage(message, timeout)

    def show_info_message(self, title: str, message: str):
        """Displays an information message box."""
        QMessageBox.information(self, title, message)

    def show_warning_message(self, title: str, message: str):
        """Displays a warning message box."""
        QMessageBox.warning(self, title, message)

    def show_critical_message(self, title: str, message: str):
        """Displays a critical error message box."""
        QMessageBox.critical(self, title, message)

    def ask_yes_no_question(self, title: str, message: str) -> bool:
        """Asks a yes/no question and returns True if Yes is selected."""
        reply = QMessageBox.question(self, title, message,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        return reply == QMessageBox.StandardButton.Yes

    def get_open_file_name(self, caption: str, filter: str) -> str:
        """Opens a file dialog for opening a file and returns the selected file path."""
        file_path, _ = QFileDialog.getOpenFileName(self, caption, "", filter)
        return file_path

    def get_save_file_name(self, caption: str, default_name: str, filter: str) -> str:
        """Opens a file dialog for saving a file and returns the selected file path."""
        file_path, _ = QFileDialog.getSaveFileName(self, caption, default_name, filter)
        return file_path

    def toggle_product_list_dock_visibility(self, visible: bool):
        """Controls the visibility of the product list dock."""
        self.available_products_dock.setVisible(visible)
        self.action_toggle_dock.setChecked(visible)