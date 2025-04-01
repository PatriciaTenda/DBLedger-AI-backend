# Ajout du répertoire parent app à sys.path avant l'importation
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import datetime
from shutil import move
from app.db.connect_to_db import Session
from app.db.crud import get_or_create_customer, create_invoice, get_or_create_product, create_invoice_item
from app.ocr_services.ocr_pipeline_runner import run_ocr_pipeline
import logging

# Dossiers
SOURCE_DIR = "data_images/images_for_extraction"
IGNORED_DIR = "data_images/data_extraction_ignored"
os.makedirs(IGNORED_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Configuration des logs
LOG_FILENAME = os.path.join("logs", "peuplement_factures_produits_items.log")
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

success, ignored, errors = 0, 0, 0

with open(LOG_FILENAME, "a", encoding="utf-8") as log:
    def log_message(msg):
        full_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
        print(full_msg)
        log.write(full_msg + "\n")

    db = Session()
    log_message("Début du peuplement complet")

    for image_filename in os.listdir(SOURCE_DIR):
        if not image_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            continue

        path = os.path.join(SOURCE_DIR, image_filename)
        log_message(f"Traitement de la facture : {image_filename}")

        try:
            extracted = run_ocr_pipeline(path)

            # Champs requis minimum
            required = ["email", "name", "birthdate", "gender", "address", "invoice_number", "issue_date", "products"]
            if not all(extracted.get(k) for k in required):
                move(path, os.path.join(IGNORED_DIR, image_filename))
                ignored += 1
                log_message(f"Incomplet → déplacé dans {IGNORED_DIR}")
                continue

            # Client
            client = get_or_create_customer(db, email=extracted["email"], data=extracted)

            # Facture
            invoice = create_invoice(db, data=extracted, customer_id=client.id_customer)

            # Produits et lignes
            for item in extracted["products"]:
                product = get_or_create_product(db, product_name=item["product"], unit_price=float(item["price"]))
                subtotal = float(item["price"]) * int(item["quantity"])
                create_invoice_item(db, invoice_id=invoice.id_invoice, product_id=product.id_product,
                                    quantity=int(item["quantity"]), subtotal=subtotal)

            db.commit()
            success += 1
            log_message(f"Facture insérée avec succès")

        except Exception as e:
            db.rollback()
            errors += 1
            move(path, os.path.join(IGNORED_DIR, image_filename))
            log_message(f"Erreur → fichier déplacé : {e}")

    db.close()
    log_message("Fin du traitement")
    log_message(f"{success} succès | {ignored} ignorés | {errors} erreurs\n")
    log_message("Fin du peuplement complet")