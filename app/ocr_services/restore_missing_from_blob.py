import sys, os
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

# Ajout du repertoire parent app à sys.path avant l'importation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Chargement des variables d’environnement
load_dotenv()
CONTAINER_URL = os.getenv("CONTAINER_URL")
CONTAINER_SAS = os.getenv("CONTAINER_SAS")

# Dossiers
DEST_DIR = "data_images/images_for_extraction"
IGNORED_DIR = "data_images/data_extraction_ignored"
os.makedirs(DEST_DIR, exist_ok=True)

downloaded = 0
skipped = 0

# Boucle sur les années
for annee in range(2018, 2025):
    print(f"\n Traitement des factures pour l'année {annee}")
    url = f"{CONTAINER_URL.strip()}/invoices-{annee}?restype=container&comp=list&{CONTAINER_SAS.strip()}"
    xml_file = f"data_images/Data/list_invoice_{annee}.xml"

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Impossible de récupérer le fichier XML pour {annee}")
        continue

    with open(xml_file, "w", encoding="utf-8") as f:
        f.write(response.text)

    tree = ET.parse(xml_file)
    root = tree.getroot()

    for blob in root.findall("Blobs/Blob"):
        image_name = blob.find("Name").text
        local_path = os.path.join(DEST_DIR, image_name)

        # Vérifie si le fichier existe déjà dans images_for_extraction ou ignored
        if os.path.exists(local_path) or os.path.exists(os.path.join(IGNORED_DIR, image_name)):
            print(f" Déjà présent : {image_name}")
            skipped += 1
            continue

        # Télécharger le fichier
        url_image = f"{CONTAINER_URL.strip()}/invoices-{annee}/{image_name}?{CONTAINER_SAS.strip()}"
        img_response = requests.get(url_image)

        if img_response.status_code == 200:
            with open(local_path, "wb") as img_file:
                img_file.write(img_response.content)
            downloaded += 1
            print(f" Téléchargé : {image_name}")
        else:
            print(f" Erreur téléchargement : {image_name}")

# Résumé
print(f"\n Téléchargements terminés : {downloaded} fichiers ajoutés, {skipped} ignorés.")
