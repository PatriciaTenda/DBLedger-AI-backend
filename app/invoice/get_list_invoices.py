import sys, os
# Ajout du repertoire parent app à sys.path avant l'importation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import requests
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from app.db import querries

# Charger les variables d'environnement
load_dotenv()

CONTAINER_URL = os.getenv("CONTAINER_URL")
CONTAINER_SAS = os.getenv("CONTAINER_SAS")


# Créer la table avant d'ajouter des factures
# Appel à create_table() pour garantir que la table existe avant d'ajouter les factures.
#querries.create_table()  

def is_data_in_database(image_id):
    # Implémentation de la vérification de l'existence de l'entrée dans la base de données
    # Retourne True si les données existent déjà
    return querries.check_invoice_exists(image_id)



# Fetching the list of invoices
for annee in range(2018, 2025):
    url =f"{CONTAINER_URL.strip()}/invoices-{annee}?restype=container&comp=list&{CONTAINER_SAS.strip()}" 
    xml_file = f"Data/list_invoice_{annee}.xml"
    reponse = requests.get(url)
    #print(url)
    #print(reponse.status_code)
    if reponse.status_code == 200 :
        xml_content = reponse.text
        #print(xml_content)
        with open(xml_file, "w") as f :
            f.write(xml_content)

    # Loard and  parse 
    #parse the file xml
    xml_tree = ET.parse(xml_file)
    root = xml_tree.getroot()
    print(root.tag)

    #Load the image name of the invoice element
    for child in root.findall("Blobs/Blob"):
        image = child.find("Name").text
        print(image)


        # update BDD
        querries.add_invoices({
                "id_invoices": image.replace("-","/")[:13],
                "name_invoices": image,
                "created_at": child.find("Properties/Creation-Time").text,
                "modified_at": child.find("Properties/Last-Modified").text,
                "content_length": int(child.find("Properties/Content-Length").text),
                "content_MD5" : child.find("Properties/Content-MD5").text
        })

        file_name_invoice = f"data_images/{image}"
        url_image = f"{CONTAINER_URL.strip()}/invoices-{annee}/{image}?{CONTAINER_SAS.strip()}"
        if  not os.path.exists(file_name_invoice): 
            reponse = requests.get(url_image)
            if reponse.status_code == 200:
                print(reponse.status_code,":",  image)
                with open(file_name_invoice,"wb") as f:
                    f.write(reponse.content)
        else:
            print(f"Les données pour l'image {image} existent déjà dans la base de données. Ignoré.")