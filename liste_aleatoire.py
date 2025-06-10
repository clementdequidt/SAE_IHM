import json
import random

with open('C:/Users/Utilisateur/Desktop/IUT/BUT1/S2/SAE/IHM/liste_produits.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

tous_les_produits = []
for categorie, produits in data.items():
    tous_les_produits.extend(produits)

# Choisir aléatoirement la taille de la liste, au moins 20, au maximum la taille totale des produits
taille_liste = random.randint(20, len(tous_les_produits))

# Générer la liste aléatoire
liste_aleatoire = random.sample(tous_les_produits, taille_liste)

for produit in liste_aleatoire:
    print(produit)
