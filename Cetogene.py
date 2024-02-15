from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower
import pyspark.sql.functions as F
import sqlite3
import pandas as pd

# Créer une session Spark
spark = SparkSession.builder.appName("DiagnostiqueRegimeVegetarien").getOrCreate()

# Charger les données depuis le fichier CSV
df = spark.read.option("header", "true").option("delimiter", "\t").csv("/home/allexxs/Téléchargements/en.openfoodfacts.org.products.csv")

# Supprimer les lignes avec un nombre important de valeurs nulles (par exemple, au moins 10 valeurs non nulles)
df = df.dropna(thresh=10)

# Imputer les valeurs manquantes pour les colonnes numériques avec la moyenne respective
for col_name in df.columns:
    if df.schema[col_name].dataType == 'double':
        mean_value = df.agg({col_name: 'mean'}).first()[0]
        df = df.na.fill(mean_value, [col_name])

# Filtrer les produits qui ne contiennent aucun glucide, n'ont pas "sucre" dans la colonne "ingredients_text",
# ont une teneur élevée en matières grasses et une teneur modérée en protéines, et où la colonne "food_groups" n'est pas nulle
df_filtered_keto = df.filter(
    (col("carbohydrates_100g") == 5) &
    (~lower(col("ingredients_text")).contains("sucre")) &
    (~lower(col("food_groups")).contains("cheese")) &
    (~lower(col("categories")).contains("condiments")) &
    (~lower(col("product_name")).contains("oil")) &
    (~lower(col("product_name")).contains("butter")) &
    (~lower(col("main_category_en")).contains("margarines")) &
    (~lower(col("quantity")).contains("ml")) &
    (~lower(col("quantity")).contains("l"))
)

# Sélectionner uniquement la colonne "product_name"
df_no_carbs_names = df_filtered_keto.select("product_name", "categories", "quantity", "food_groups", "carbohydrates_100g", "sodium_100g")

# Séparer les produits en plats et desserts en fonction de la colonne "food_groups"
df_plats = df_no_carbs_names.filter(col("categories").contains("plats"))
df_desserts = df_no_carbs_names.filter(col("categories").contains("desserts"))

# Afficher les premières lignes des DataFrames pour les plats et les desserts
print("\nPlats adaptés au régime cétogène :")
df_plats.show(truncate=False)

print("\nDesserts adaptés au régime cétogène :")
df_desserts.show(truncate=False)


# Afficher les premières lignes du DataFrame après le nettoyage et le filtrage
print("\nProduits adaptés au régime Végétarien :")
df_no_carbs_names.show(20,truncate=False)
# Initialiser la liste products_data avant la boucle

# Initialiser la liste products_data avant la boucle
products_data = []
# Générer 2 repas par jour pour 7 jours
for day in range(1, 2):
    print(f"\nJour {day} :")

    # Sélectionner aléatoirement un plat pour chaque repas
    plat1_row = df_plats.orderBy(F.rand()).limit(1).select("product_name", "categories", "quantity", "food_groups", "carbohydrates_100g", "sodium_100g").first()
    plat2_row = df_plats.orderBy(F.rand()).limit(1).select("product_name", "categories", "quantity", "food_groups", "carbohydrates_100g", "sodium_100g").first()

    # Sélectionner aléatoirement un dessert pour chaque repas
    dessert1_row = df_desserts.orderBy(F.rand()).limit(1).select("product_name", "categories", "quantity", "food_groups", "carbohydrates_100g", "sodium_100g").first()
    dessert2_row = df_desserts.orderBy(F.rand()).limit(1).select("product_name", "categories", "quantity", "food_groups", "carbohydrates_100g", "sodium_100g").first()

    plat1 = plat1_row["product_name"]
    plat1_categories = plat1_row["categories"]
    plat1_quantity = plat1_row["quantity"]
    plat1_food_groups = plat1_row["food_groups"]
    plat1_glucides = plat1_row["carbohydrates_100g"]
    plat1_sodium = plat1_row["sodium_100g"]

    plat2 = plat2_row["product_name"]
    plat2_categories = plat2_row["categories"]
    plat2_quantity = plat2_row["quantity"]
    plat2_food_groups = plat2_row["food_groups"]
    plat2_glucides = plat2_row["carbohydrates_100g"]
    plat2_sodium = plat2_row["sodium_100g"]

    dessert1 = dessert1_row["product_name"]
    dessert1_categories = dessert1_row["categories"]
    dessert1_quantity = dessert1_row["quantity"]
    dessert1_food_groups = dessert1_row["food_groups"]
    dessert1_glucides = dessert1_row["carbohydrates_100g"]
    dessert1_sodium = dessert1_row["sodium_100g"]

    dessert2 = dessert2_row["product_name"]
    dessert2_categories = dessert2_row["categories"]
    dessert2_quantity = dessert2_row["quantity"]
    dessert2_food_groups = dessert2_row["food_groups"]
    dessert2_glucides = dessert2_row["carbohydrates_100g"]
    dessert2_sodium = dessert2_row["sodium_100g"]

    print(f"  Petit-déjeuner : Plat - {plat1}, Dessert - {dessert1}")
    print(f"  Dîner : Plat - {plat2}, Dessert - {dessert2}")

    # Ajouter les données générées à la liste
    products_data.extend([
        (plat1, 'cetogene', plat1_quantity, 'plats', plat1_glucides, plat1_sodium, 3),
        (dessert1, 'cetogene', dessert1_quantity, 'desserts', dessert1_glucides, dessert1_sodium, 3),
        (plat2, 'cetogene', plat2_quantity, 'plats', plat2_glucides, plat2_sodium, 3),
        (dessert2, 'cetogene', dessert2_quantity, 'desserts', dessert2_glucides, dessert2_sodium, 3),
    ])

# Connexion à la base de données SQLite
conn = sqlite3.connect("../Food.sqlite")
cursor = conn.cursor()

# Création de la table ProduitOpenFoodFacts si elle n'existe pas
cursor.execute("""
CREATE TABLE IF NOT EXISTS ProduitsOpenFoodFacts (
    produit_id INTEGER PRIMARY KEY,
    product_name TEXT,
    categories TEXT,
    food_groups TEXT
);
""")

# Insérer les données générées dans la table existante ProduitOpenFoodFacts
cursor.executemany("""
INSERT INTO ProduitsOpenFoodFacts (product_name, categories, quantity, food_groups, glucides, sodium, programme_alimentaire_id) VALUES (?, ?, ?, ?, ?, ?, ?);
""", products_data)

# Commit pour valider les changements dans la base de données
conn.commit()