# MVC_CONTROLLER.py
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap
from MVC_MODEL import StoreModel # Assuming model is in MVC_MODEL.py
from MVC_VIEW import FenetreAppliView # Assuming view is in MVC_VIEW.py

class StoreController:
    def __init__(self, model: StoreModel, view: FenetreAppliView):
        self._model = model
        self._view = view
        self._connect_signals()
        self._update_view_from_model() # Initial view update

    def _connect_signals(self):
        """Connects UI signals to controller slots."""
        self._view.open_plan_action.triggered.connect(self.handle_open_store_plan)
        self._view.quit_action.triggered.connect(QApplication.instance().quit)
        self._view.action_toggle_dock.triggered.connect(self.handle_toggle_product_list_dock)
        self._view.add_to_list_btn.clicked.connect(self.handle_add_selected_to_shopping_list)
        self._view.remove_from_list_btn.clicked.connect(self.handle_remove_selected_from_shopping_list)
        self._view.clear_list_btn.clicked.connect(self.handle_clear_shopping_list)
        self._view.save_list_btn.clicked.connect(self.handle_save_shopping_list)

    def _update_view_from_model(self):
        """Updates all parts of the view based on the current model state."""
        self._view.update_store_info(self._model.store_info)
        
        if self._model.map_image_path:
            self._view.display_map(QPixmap(self._model.map_image_path))
        else:
            # Clear map if no image is set (e.g., after initial load or error)
            self._view.image_viewer.set_map_pixmap(QPixmap()) 

        self._view.display_available_products(self._model.available_products)
        self._view.display_product_positions_on_map(self._model.product_positions)
        self._view.update_shopping_list_display(self._model.shopping_list)

    # --- Handlers for UI actions (Controller's role) ---
    def handle_open_store_plan(self):
        """Handles the action to open a store plan."""
        self._view.show_status_message('Opening store plan...', 2000)
        file_path = self._view.get_open_file_name(
            "Open Saved Store Plan",
            "Store Files (*.json)"
        )
        if file_path:
            success, message = self._model.load_store_plan(file_path)
            if success:
                self._update_view_from_model()
                self._view.show_status_message(message, 3000)
            else:
                self._view.show_critical_message("File Error", message)
                self._view.show_status_message('Failed to load store plan.', 2000)
        else:
            self._view.show_status_message('Store plan opening cancelled.', 2000)

    def handle_toggle_product_list_dock(self):
        """Handles toggling the visibility of the product list dock."""
        is_visible = self._view.available_products_dock.isVisible()
        self._view.toggle_product_list_dock_visibility(not is_visible)
        if not is_visible:
            self._view.show_status_message("Product panel displayed.", 2000)
        else:
            self._view.show_status_message("Product panel hidden.", 2000)

    def handle_add_selected_to_shopping_list(self):
        """Adds selected items from available products to the shopping list."""
        selected_items = self._view.available_products_list_widget.selectedItems()
        if not selected_items:
            self._view.show_info_message("Empty Selection", "Please select at least one product to add.")
            return

        added_count = 0
        for item in selected_items:
            product_name = item.text()
            if not product_name.startswith("---"): # Avoid adding category headers
                self._model.add_product_to_shopping_list(product_name)
                added_count += 1
        
        self._view.update_shopping_list_display(self._model.shopping_list)
        if added_count > 0:
            self._view.show_status_message(f"{added_count} products added to shopping list.", 2000)
        else:
            self._view.show_status_message("No products added to shopping list.", 2000)


    def handle_remove_selected_from_shopping_list(self):
        """Removes selected items from the shopping list."""
        selected_items = self._view.shopping_list_widget.selectedItems()
        if not selected_items:
            self._view.show_info_message("Empty Selection", "Please select at least one product to remove.")
            return
        
        products_to_remove = [item.text() for item in selected_items]
        self._model.remove_products_from_shopping_list(products_to_remove)
        self._view.update_shopping_list_display(self._model.shopping_list)
        self._view.show_status_message(f"{len(selected_items)} products removed from shopping list.", 2000)

    def handle_clear_shopping_list(self):
        """Clears all items from the shopping list."""
        if not self._model.shopping_list:
            self._view.show_info_message("Empty List", "The shopping list is already empty.")
            return

        if self._view.ask_yes_no_question('Clear List', "Are you sure you want to clear the entire shopping list?"):
            self._model.clear_shopping_list()
            self._view.update_shopping_list_display(self._model.shopping_list)
            self._view.show_status_message("Shopping list cleared.", 2000)

    def handle_save_shopping_list(self):
        """Saves the current shopping list to a text file."""
        if not self._model.shopping_list:
            self._view.show_info_message("Empty List", "The shopping list is empty and cannot be saved.")
            return

        file_path = self._view.get_save_file_name(
            "Save Shopping List",
            "my_shopping_list.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            success, message = self._model.save_shopping_list(file_path)
            if success:
                self._view.show_status_message(message, 3000)
                self._view.show_info_message("Save Successful", f"Your shopping list has been saved to:\n{file_path}")
            else:
                self._view.show_critical_message("Save Error", message)