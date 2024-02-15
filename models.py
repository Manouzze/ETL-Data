from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Session

Base = declarative_base()

class RegimeAlimentaire(Base):
    __tablename__ = 'RegimesAlimentaires'
    programme_alimentaire_id = Column(Integer, primary_key=True)
    nom_programme = Column(String)
    calories_max = Column(Float)
    sodium_max = Column(Float)
    glucides_max = Column(Float)
    utilisateurs = relationship('Utilisateur', back_populates='regime_alimentaire')
    produits = relationship('ProduitOpenFoodFacts', back_populates='regime_alimentaire')

class Utilisateur(Base):
    __tablename__ = 'Utilisateurs'
    utilisateur_id = Column(Integer, primary_key=True)
    nom = Column(String)
    age = Column(Integer)
    sexe = Column(String)
    poids = Column(Float)
    programme_alimentaire_id = Column(Integer, ForeignKey('RegimesAlimentaires.programme_alimentaire_id'))

    regime_alimentaire = relationship('RegimeAlimentaire', back_populates='utilisateurs')
    menus = relationship('MenuHebdomadaire', back_populates='utilisateur')

class ProduitOpenFoodFacts(Base):
    __tablename__ = 'ProduitsOpenFoodFacts'
    produit_id = Column(Integer, primary_key=True)
    product_name = Column(String)
    categories = Column(String)
    quantity = Column(Float)
    food_groups = Column(String)
    glucides = Column(Float)
    sodium = Column(Float)
    programme_alimentaire_id = Column(Integer, ForeignKey('RegimesAlimentaires.programme_alimentaire_id'))
    regime_alimentaire = relationship('RegimeAlimentaire', back_populates='produits')
    menus = relationship('MenuHebdomadaire', back_populates='produit')

class MenuHebdomadaire(Base):
    __tablename__ = 'MenuHebdomadaire'
    menu_id = Column(Integer, primary_key=True)
    utilisateur_id = Column(Integer, ForeignKey('Utilisateurs.utilisateur_id'))
    jour_semaine = Column(String)
    produit_id = Column(Integer, ForeignKey('ProduitsOpenFoodFacts.produit_id'))

    utilisateur = relationship('Utilisateur', back_populates='menus')
    produit = relationship('ProduitOpenFoodFacts', back_populates='menus')


# Création d'une instance de régime végétarien
regime_vegetarien = RegimeAlimentaire(
    nom_programme="Végétarien",
    sodium_max=2300,
    glucides_max=275
)
regime_vegetalien = RegimeAlimentaire(
    nom_programme="Végétalien",
    sodium_max=2300,
    glucides_max=275
)
regime_cetogene = RegimeAlimentaire(
    nom_programme="Cétogène",
    sodium_max=2300,
    glucides_max=275
)

# Création d'une instance d'utilisateur associée au régime végétarien
utilisateur_vegetarien = Utilisateur(
    nom="Utilisateur Végétarien",
    age=30,
    sexe="F",
    poids=65,
    regime_alimentaire=regime_vegetarien
)

# Création d'une instance de produit OpenFoodFacts associée au régime végétarien
produit_vegetalien = ProduitOpenFoodFacts(
    product_name="TANDOORI NAANS x1",
    sodium=200,
    glucides=50,
    categories="vegetalien",
    food_groups="plat",
    regime_alimentaire=regime_vegetarien
)

# Création d'une instance de menu hebdomadaire
menu_hebdo_vegetarien = MenuHebdomadaire(
    utilisateur=utilisateur_vegetarien,
    jour_semaine="Lundi",
    produit=produit_vegetalien
)

# Utilisation d'une session SQLAlchemy pour enregistrer les objets dans la base de données
engine = create_engine('sqlite:///Food.sqlite')
Base.metadata.create_all(engine)

session = Session(engine)
session.add(regime_vegetarien)
session.add(regime_vegetalien)
session.add(utilisateur_vegetarien)
session.add(produit_vegetalien)
session.add(menu_hebdo_vegetarien)
session.commit()
session.close()
