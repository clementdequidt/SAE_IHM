# MVC_MODEL.py
import json
import os
from collections import defaultdict

class StoreModel:
    def __init__(self):
        self._store_info = {
            "nom_magasin": "Aucun plan chargé",
            "auteur": "N/A",
            "adresse_magasin": "N/A"
        }
        self._map_image_path = None
        self._available_products = defaultdict(list) # Category -> [product names]
        self._product_positions = {} # Product name -> {'x': float, 'y': float}
        self._shopping_list = [] # List of product names

    # --- Properties to access data ---
    @property
    def store_info(self):
        return self._store_info

    @property
    def map_image_path(self):
        return self._map_image_path

    @property
    def available_products(self):
        return self._available_products

    @property
    def product_positions(self):
        return self._product_positions

    @property
    def shopping_list(self):
        return self._shopping_list[:] # Return a copy to prevent external modification

    # --- Data Loading / Saving ---
    def load_store_plan(self, file_path: str):
        """
        Loads store plan data from a JSON file.
        Returns (success: bool, message: str)
        """
        if not file_path:
            return False, "Opening cancelled."

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)

            # Update store info
            self._store_info = project_data.get("questionnaire_info", {})
            
            # Update map image path
            image_path = project_data.get("chemin_image_plan")
            if not os.path.exists(image_path):
                return False, f"Map image '{image_path}' not found. Please check the path or load another plan."
            self._map_image_path = image_path

            # Update available products
            self._available_products = defaultdict(list, project_data.get("produits_selectionnes", {}))

            # Update product positions
            self._product_positions = project_data.get("positions_produits_finales", {})
            
            # Clear shopping list when a new store plan is loaded
            self._shopping_list.clear()

            return True, f"Store plan loaded successfully from {file_path}"

        except json.JSONDecodeError:
            return False, "Selected file is not a valid JSON file."
        except Exception as e:
            return False, f"Failed to load store plan: {e}"

    def add_product_to_shopping_list(self, product_name: str):
        """Adds a product to the shopping list."""
        self._shopping_list.append(product_name)

    def remove_products_from_shopping_list(self, product_names: list[str]):
        """Removes specified products from the shopping list.
        If multiple instances of the same product exist, it removes one instance per name provided.
        """
        for product_name in product_names:
            if product_name in self._shopping_list:
                self._shopping_list.remove(product_name)

    def clear_shopping_list(self):
        """Clears all products from the shopping list."""
        self._shopping_list.clear()

    def save_shopping_list(self, file_path: str):
        """
        Saves the current shopping list to a text file.
        Returns (success: bool, message: str)
        """
        if not self._shopping_list:
            return False, "Shopping list is empty and cannot be saved."

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for product in self._shopping_list:
                    f.write(product + '\n')
            return True, f"Shopping list saved to {file_path}"
        except Exception as e:
            return False, f"Failed to save shopping list: {e}"