import numpy as np
import cv2
from pyzbar.pyzbar import decode


def extract_qr_data(image):
    decoded = decode(image)
    if decoded:
        return decoded[0].data.decode("utf-8")
    return None

"""
# get the image path
image_path = r"data_images\images_for_test\FAC_2018_0001-654.png"
image_ = cv2.imread(image_path)
qr_extract = extract_qr_data(image_)
print(" Texte brut du QR code :", qr_extract)"
"""