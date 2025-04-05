# Ajout du répertoire parent app à sys.path avant l'importation
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.db.models import t_customer, t_invoice, t_product, t_invoice_item
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import func, desc
from sqlalchemy.exc import IntegrityError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ───── CLIENT ─────
def get_or_create_customer(db: Session, email: str, data: dict):
    try:
        customer = db.query(t_customer).filter_by(email_customer=email).first()
        if customer:
            return customer

        customer = t_customer(
            email_customer=email,
            name_customer=data["name"],
            date_of_birth_customer=data["birthdate"],
            sexe_customer=data["gender"],
            address_customer=data["address"]
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        logger.info(f"[CLIENT] Ajouté : {customer.name_customer} | Email : {customer.email_customer}")
        return customer
    except IntegrityError:
        db.rollback()
        logger.warning(f"[CLIENT] Échec d'insertion (doublon ou erreur) : {email}")
        return db.query(t_customer).filter_by(email_customer=email).first()

# ───── FACTURE ─────
def create_invoice(db: Session, data: dict, customer_id: int):
    try:
        existing = db.query(t_invoice).filter_by(id_invoice=data["invoice_number"]).first()
        if existing:
            return existing

        invoice = t_invoice(
            id_invoice=data["invoice_number"],
            id_customer=customer_id,
            name_invoice=None,
            created_at=None,
            modified_at=None,
            content_length=0,
            content_md5="unknown",
            issue_date=datetime.strptime(data["issue_date"], "%Y-%m-%d"),
            total_amount=data.get("total")
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        logger.info(f"[FACTURE] Ajoutée : {invoice.id_invoice}")
        return invoice
    except IntegrityError:
        db.rollback()
        logger.warning(f"[FACTURE] Doublon ignoré : {data['invoice_number']}")
        return db.query(t_invoice).filter_by(id_invoice=data["invoice_number"]).first()

# ───── PRODUIT ─────
def get_or_create_product(db: Session, product_name: str, unit_price: float):
    try:
        product = db.query(t_product).filter_by(name_product=product_name, unit_price=unit_price).first()
        if product:
            return product

        product = t_product(name_product=product_name, unit_price=unit_price)
        db.add(product)
        db.commit()
        db.refresh(product)
        logger.info(f"[PRODUIT] Ajouté : {product.name_product}")
        return product
    except IntegrityError:
        db.rollback()
        logger.warning(f"[PRODUIT] Doublon ignoré : {product_name}")
        return db.query(t_product).filter_by(name_product=product_name, unit_price=unit_price).first()

# ───── LIGNE DE FACTURE ─────
def create_invoice_item(db: Session, invoice_id: str, product_id: int, quantity: int, subtotal: float):
    try:
        item = t_invoice_item(
            id_invoice=invoice_id,
            id_product=product_id,
            quantities=quantity,
            subtotals=subtotal
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        logger.info(f"[LIGNE] Ajoutée : facture {invoice_id} - produit {product_id}")
        return item
    except IntegrityError:
        db.rollback()
        logger.warning(f"[LIGNE] Doublon ou erreur d'insertion : {invoice_id} | produit {product_id}")
        return None


