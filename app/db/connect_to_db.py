from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


# Chargement des variables d'environnement 
load_dotenv()

# Récupération de l'URL de la base de données
POSTGRES_URL = os.getenv("POSTGRES_URL")

# Vérification que l'URL de la base de données a bien été chargée
if  not POSTGRES_URL:
    print("Erreur: L'URL de la base de données n'est pas définie dans les variables d'environnement.")
    exit(1)

# Création du moteur SQLAlchimy
engine = create_engine(POSTGRES_URL)

def db_connexion():
    try:
        conn = engine.connect()
        print(f"Connexion réussie !")
        return conn
    except Exception as e:
        print(f"Erreur de connexion {e}")
        return None
    


