import random
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Session
from models import ProduitOpenFoodFacts, MenuHebdomadaire, RegimeAlimentaire
import sqlite3
Base = declarative_base()
conn = sqlite3.connect("Food.sqlite")
cur = conn.cursor()



def generer_repas(session, utilisateur_id, regime_alimentaire, nb_repas_par_jour, nb_jours):
    # Récupérer les produits correspondant au régime alimentaire de l'utilisateur
    conn = sqlite3.connect("Food.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ProduitsOpenFoodFacts WHERE categories = ?", (regime_alimentaire,))
    produits = cursor.fetchall()

    if not produits:
        print(f"Aucun produit trouvé pour le régime alimentaire {regime_alimentaire}")
        return
    produits = [ProduitOpenFoodFacts(product_name=row[1], categories=row[2], quantity=row[3], food_groups=row[4],
                                     glucides=row[5], sodium=row[6]) for row in produits]

    # Séparer les produits en plats et desserts
    plats = [produit for produit in produits if produit.food_groups == 'plats']
    desserts = [produit for produit in produits if produit.food_groups == 'desserts']

    if not plats or not desserts:
        print(f"Aucun plat ou dessert trouvé pour le régime alimentaire {regime_alimentaire}")
        return


    # Générer les repas pour chaque jour
    for jour in range(1, nb_jours + 1):
        print(f"\nJour {jour} :")
        for repas in range(1, nb_repas_par_jour + 1):
            # Sélectionner aléatoirement un plat et un dessert
            plat = random.choice(plats)
            dessert = random.choice(desserts)

            # Insérer le repas pour l'utilisateur dans la table MenuHebdomadaire
            menu_repas = MenuHebdomadaire(utilisateur_id=utilisateur_id, jour_semaine=f"Jour {jour}", produit_id=plat.produit_id)
            menu_dessert = MenuHebdomadaire(utilisateur_id=utilisateur_id, jour_semaine=f"Jour {jour}", produit_id=dessert.produit_id)

            session.add_all([menu_repas, menu_dessert])

            print(f"  Repas {repas} : Plat - {plat.product_name}, Dessert - {dessert.product_name}")

    # Commit des changements
    session.commit()

# Exemple d'utilisation
engine = create_engine('sqlite:///Food.sqlite')
Base.metadata.create_all(engine)
session = Session(engine)

# Ajoutez votre utilisateur et son régime alimentaire ici avant de lancer la fonction generer_repas

utilisateur_id = 2  # Remplacez par l'id de votre utilisateur
regime_alimentaire = "vegetarien"  # Remplacez par le régime alimentaire de votre utilisateur
nb_repas_par_jour = 2
nb_jours = 7

generer_repas(session, utilisateur_id, regime_alimentaire, nb_repas_par_jour, nb_jours)
session = Session(engine)
session.commit()
session.close()