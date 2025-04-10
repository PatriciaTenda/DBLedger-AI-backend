from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os
from contextlib import contextmanager


# Chargement des variables d'environnement 
load_dotenv()

# Récupération de l'URL de la base de données
POSTGRES_URL = os.getenv("POSTGRES_URL")

# Vérification que l'URL de la base de données a bien été chargée
if  not POSTGRES_URL:
    print("Erreur: L'URL de la base de données n'est pas définie dans les variables d'environnement.")
    exit(1)

# Création du moteur SQLAlchimy
engine = create_engine(POSTGRES_URL, echo=True,
                       connect_args={"connect_timeout": 30, 'options': '-csearch_path=patricia'},
                      )
# Créer un générateur de session
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuration de la Base
Base = declarative_base(metadata=MetaData(schema="patricia"))

def db_connexion():
    try:
        conn = engine.connect()
        print(f"Connexion réussie !")
        return conn
    except Exception as e:
        print(f"Erreur de connexion {e}")
        return None

@contextmanager    
def get_session():
    # Créer une session locale pour des opérations sur la base et s'assure que la session est bien fermée
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()



