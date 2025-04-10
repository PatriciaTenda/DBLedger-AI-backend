import sys, os
# Ajout du repertoire parent app à sys.path avant l'importation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.ocr_services.data_parser import extract_all_invoice_data
import cv2, json
from app.ocr_services.ocr_engine import extract_text_from_image
from app.ocr_services.qrcode_reader import extract_qr_data
from app.ocr_services.ocr_preprocessing import preprocess_image, mask_qr_code
from app.ocr_services.ocr_engine import extract_text_from_image
from app.ocr_services.qrcode_reader import extract_qr_data



def run_ocr_pipeline(image_path: str):
    """
    Concatène le texte extrait par OCR et le QR code.
    """
    print(" Lecture de l'image :", image_path)
    image_cv = cv2.imread(image_path)

    # Prétraitement
    image_without_qrcode = mask_qr_code(image_cv)

    preprocessed_pil = preprocess_image(image_without_qrcode)

    # OCR
    ocr_text = extract_text_from_image(preprocessed_pil)
    print("\n Texte OCR :\n", ocr_text)

      # QR code
    qr_text = extract_qr_data(image_cv)
    print("\n Texte QR brut :\n", qr_text)


    text = ocr_text.strip() + "\n\n" + (qr_text.strip() if qr_text else "")


    # Parsing
    all_data = extract_all_invoice_data(text)

    print("\n Données prêtes pour la base :")
    print(json.dumps(all_data, indent=4, ensure_ascii=False))
    return all_data

def export_to_json(data: dict, file_path: str = "extracted_invoice.json"):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Données exportées dans {file_path}")

#Exemple d'exécution
if __name__ == "__main__":
    print("\nDonnées extraites pour la base :")
    result = run_ocr_pipeline("data_images/images_for_test/FAC_2018_0001-654.png")
    print(result)
    export_to_json(result)
    