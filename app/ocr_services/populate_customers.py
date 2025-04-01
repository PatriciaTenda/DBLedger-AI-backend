import sys, os
# Ajout du repertoire parent app à sys.path avant l'importation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from shutil import move
from datetime import datetime
from app.ocr_services.ocr_pipeline_runner import run_ocr_pipeline
from app.db.crud import get_or_create_customer
from app.db.connect_to_db import Session
import logging


# Dossiers
SOURCE_DIR = "data_images/images_for_extraction"
IGNORED_DIR = "data_images/data_extraction_ignored"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "peuplement_clients.log")

# Création des dossiers nécessaires
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(IGNORED_DIR, exist_ok=True)

# Backup automatique du log précédent
if os.path.exists(LOG_FILE):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.rename(LOG_FILE, os.path.join(LOG_DIR, f"peuplement_clients_backup_{timestamp}.log"))

# Configuration du logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialisation des compteurs
success_count = 0
ignored_count = 0
error_count = 0

# Ouvrir le fichier de log
with open(LOG_FILE, "a", encoding="utf-8") as log:
    def log_message(msg):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        full_msg = f"{timestamp} {msg}\n"
        print(full_msg.strip())  # Affiche dans la console
        log.write(full_msg)

    # Connexion à la base
    db = Session()

    log_message("Début du peuplement de la table t_customer")

    for filename in os.listdir(SOURCE_DIR):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            continue

        file_path = os.path.join(SOURCE_DIR, filename)
        log_message(f"Traitement : {filename}")

        try:
            extracted = run_ocr_pipeline(file_path)

            required_fields = ["email", "name", "birthdate", "gender", "address"]
            if not all(extracted.get(field) for field in required_fields):
                move(file_path, os.path.join(IGNORED_DIR, filename))
                ignored_count += 1
                log_message(f"Incomplet : {filename} déplacé dans {IGNORED_DIR}")
                continue

            get_or_create_customer(db, email=extracted["email"], data=extracted)
            db.commit()
            success_count += 1
            log_message(f"Client inséré depuis : {filename}")

        except Exception as e:
            db.rollback()
            move(file_path, os.path.join(IGNORED_DIR, filename))
            error_count += 1
            log_message(f"Erreur : {filename} déplacé. Détail : {e}")

    db.close()

    # Résumé final
    log_message("Fin du traitement des clients")
    log_message(f"Résumé : {success_count} clients insérés, {ignored_count} ignorés, {error_count} erreurs.\n")
    log_message("Fin du peuplement de la table t_customer")