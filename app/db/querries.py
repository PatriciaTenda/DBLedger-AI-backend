import sys, os
# Ajout du repertoire parent app à sys.path avant l'importation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from  app.db.connect_to_db import db_connexion
from  sqlalchemy import text


def create_table():
    conn = db_connexion()
        
    if conn: 
          
        try:
            with conn.begin():# Utilisation de transaction sécurisée
                conn.execute(text("SET search_path TO patricia;"))  # Pour s'assurer que le schéma est bien utilisé
                create_table_query = """
                CREATE TABLE IF NOT EXISTS t_invoices (
                id_invoices VARCHAR(50) PRIMARY KEY,
                name_invoices VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                content_length INT,
                content_MD5 VARCHAR(100) NOT NULL
                ); 
                                        
                """
                conn.execute(text(create_table_query))
                #conn.commit() # Valider la création de la table
                print("Table invoices créée avec succès !")

                # Vérifier si la table est bien créée
                tables = conn.execute(text("SELECT tablename  FROM pg_catalog.pg_tables WHERE schemaname = 'patricia';")).fetchall()
                print("Tables existantes dans le schéma patricia:", tables)
            
        except Exception as e:
            print(f"Erreur lors de la création de la table , {e}")
            
        finally:
            conn.close()



def add_invoices(obj):
    conn = db_connexion()
    
    if conn: 
        try:
            with conn.begin():
                conn.execute(text("SET search_path TO patricia;"))  # Pour s'assurer que le schéma est bien utilisé
                add_invoice_query = """
                INSERT INTO t_invoices(
                id_invoices,
                name_invoices,
                created_at,
                modified_at,
                content_length,
                content_MD5 
                ) values (:id_invoices, :name_invoices, :created_at, :modified_at, :content_length, :content_MD5)
                ON CONFLICT(id_invoices) DO NOTHING;                       
                """
                conn.execute(text(add_invoice_query), obj) # Utilisation des paramètres fournis
                #conn.commit() # Ajout du commit pour enregistrer les chargements
                print("Enregistrement effectués avec succès !")
            
        except Exception as e:
            print(f"Erreur lors de lors de l'enregistrement des donnéesdans la table invoices, {e}")
            
        finally:
            conn.close()


def check_invoice_exists(invoice_id):
    conn = db_connexion()
    try:
        with conn.begin():
            conn.execute(text("SET search_path TO patricia;"))
            # Implémentation pour vérifier dans la base de données
            query = "SELECT COUNT(*) FROM t_invoices WHERE id_invoices = :invoice_id"
            result = conn.execute(text(query), {"invoice_id": invoice_id}).fetchone()
            #print(f"Voici le resultat ==>{result[0]}")
            return result[0] > 0  # Vérifie si la facture existe
    except Exception as e:
        print(f"Erreur lors de l'exécution, {e}")
    finally:
        conn.close()


check_invoice_exists("FAC_2025_0001")

#create_table()
"""
add_invoices({
    "id_invoices": "FAC_2025_0001",
    "name_invoices": "FAC_2025_0001-654.png",
    "created_at": "2025-03-12 10:00:00",
    "modified_at": "2025-03-12 10:00:00",
    "content_length": 77748,
    "content_MD5": "3hGVR9yLMRMDdDaHE7dAEA=="
})
"""

