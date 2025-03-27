import sys, os
# Ajout du repertoire parent app à sys.path avant l'importation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import re

# ------------------------- PARSERS -------------------------- #

def parse_invoice_fields(text: str) -> dict:
    data = {}
    match = re.search(r"INVOICE\s+([A-Z]+/\d{4}/\d+)", text)
    if match:
        data["invoice_number"] = match.group(1)
    match = re.search(r"Issue date\s+(\d{4}-\d{2}-\d{2})", text)
    if match:
        data["issue_date"] = match.group(1)
    match = re.search(r"TOTAL\s+([\d.,\s]+)\s*(\w+)?", text, re.IGNORECASE)
    if match:
        data["total"] = match.group(1).replace(",", ".").replace(" ", "")
        data["currency"] = match.group(2).upper() if match.group(2) else "UNSPECIFIED"
    return data


def parse_customer_fields(text: str) -> dict:
    data = {}
    match = re.search(r"Bill to\s+([A-Za-z ]+)", text)
    if match:
        data["name"] = match.group(1).strip()
    match = re.search(r"Email\s+([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", text)
    if match:
        data["email"] = match.group(1)

    # --- Extraction d'adresse plus robuste ---
    lines = text.splitlines()
    
    for i, line in enumerate(lines):
        if "address" in line.lower():
            address_line = line.strip()
            if address_line.lower().startswith("address"):
                address_line = address_line[len("address"):].strip()

            # Commencer à construire l'adresse
            address_parts = [address_line]

            # Regarder les 1 à 2 lignes suivantes (si elles ne sont pas des produits)
            for j in range(i+1, min(i+3, len(lines))):
                next_line = lines[j].strip()
                if next_line and "x" not in next_line.lower():
                    address_parts.append(next_line)

            full_address = ", ".join(address_parts)
            data["address"] = full_address
            break

    match = re.search(r"CUST[:\s]*([MF]),\s*birth\s+(\d{4}-\d{2}-\d{2})", text, re.IGNORECASE)
    if match:
        data["gender"] = match.group(1)
        data["birthdate"] = match.group(2)
    return data


def parse_product_list(text: str) -> list:
    pattern = r"(.+?)\s+(\d+)\s*[xX]\s*([\d.,]+)\s*(Euro|EUR|\u20ac)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    products = []
    for match in matches:
        name = match[0].strip().rstrip(".")
        quantity = int(match[1])
        price = match[2].replace(",", ".")
        currency = match[3].upper().replace("EURO", "EUR").replace("\u20ac", "EUR")
        products.append({
            "product": name,
            "quantity": quantity,
            "price": price,
            "currency": currency
        })
    return products


# ---------------------- PIPELINE FINAL ---------------------- #

def extract_all_invoice_data(text: str) -> dict:
    data = {}
    data.update(parse_invoice_fields(text))
    data.update(parse_customer_fields(text))
    data["products"] = parse_product_list(text)
    return data


"""
if __name__ == "__main__":
    image_path = "data_images/images_for_test/FAC_2018_0001-654.png"
    result = extract_all_invoice_data(image_path)
    print("\nDonnées extraites pour la base :")
    print(result)
"""