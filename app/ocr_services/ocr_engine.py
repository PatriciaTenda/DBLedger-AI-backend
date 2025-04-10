import sys, os
# Ajout du repertoire parent app à sys.path avant l'importation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from PIL import Image
import pytesseract, cv2

 
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_image(image_thresh):
    
# 1. Convertir OpenCV → PIL
    pil_image = Image.fromarray(image_thresh)

# 2. (Optionnel) Renforcer un peu le contraste
    #pil_image = ImageEnhance.Contrast(pil_image).enhance(2.0)

    custom_config = r'--oem 3 --psm 6'
    
    return pytesseract.image_to_string(pil_image, lang="eng", config=custom_config)



"""
preprocessed_image =  r"resultat_pretraite.png"
image = cv2.imread(preprocessed_image) 
texte = extract_text_from_image(image)
print(texte)
"""


