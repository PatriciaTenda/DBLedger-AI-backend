import sys, os
# Ajout du repertoire parent app à sys.path avant l'importation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import cv2


def mask_qr_code(image):
    x, y, w, h = 528, 10, 300, 150
    masked = image.copy()
    cv2.rectangle(masked, (x, y), (x + w, y + h), (255, 255, 255), -1)
    return masked

def preprocess_image(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Seuillage adaptatif
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 10)
    # Zoom si l'image est trop petite
    height, width = thresh.shape[:2]
    if width < 1000 or height < 800:
        print(f"Image trop petite ({width}x{height}) → agrandissement")
        scale = 2
        thresh = cv2.resize(thresh, (width * scale, height * scale), interpolation=cv2.INTER_CUBIC)
    return thresh


"""
print("**********************************************************************************************************************************************")
# get the image path
image_path = r"data_images\images_for_test\FAC_2018_0001-654.png"
image = cv2.imread(image_path)
image_masquée=mask_qr_code(image)

#cv2.imshow("Image masquée", image_masquée)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

# Appliquer le prétraitement
preprocessed_image = preprocess_image(image_masquée)

# Afficher l’image prétraitée
cv2.imshow("Image prétraitée (sans QR)", preprocessed_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
print("Répertoire courant :", os.getcwd())
cv2.imwrite("resultat_pretraite.png", preprocessed_image)
"""
