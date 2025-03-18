import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..")))

from sqlalchemy import create_engine,Column,Integer,String,ForeignKey,Date,DateTime, DECIMAL, CheckConstraint,func
from sqlalchemy.orm import declarative_base, relationship
from app.db.connect_to_db import Base


# Update invoices table
class t_invoice(Base):
    __tablename__ = 't_invoice'
    __table_args__ = (        
                        {"schema": "patricia"},
                      
                      )   # Spécifier le schéma

    id_invoice = Column(String, primary_key=True)
    id_customer = Column(Integer, ForeignKey("patricia.t_customer.id_customer"), nullable=False)
    name_invoice = Column(String, nullable= False)
    created_at = Column(DateTime, nullable= False)
    modified_at = Column(DateTime, nullable= False)
    content_length = Column(Integer, nullable= False)
    content_md5 = Column(String, nullable= False)
    issue_date = Column(DateTime, nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=True)
    
    # Plusieurs factures peuvent appartenir à un seul client
    customer = relationship("t_customer", back_populates="invoice")

    # Une facture peut contenir plusieurs lignes de facturation.
    # Relation plusieurs-à-plusieurs avec t_products via la table t_invoices_items
    # Relation avec la table d'association
    invoice_item = relationship("t_invoice_item", back_populates="invoice", cascade="all, delete")


    def __repr__(self):
       return f"INVOICE n°{self.id_invoice} Invoice name : {self.name_invoice})"
    

class t_customer(Base):
    __tablename__ = 't_customer'
    __table_args__ = ({"schema": "patricia"},)   # Spécifier le schéma

    id_customer = Column(Integer, primary_key=True, autoincrement=True)
    email_customer = Column(String(255), unique=True, nullable=True)
    name_customer = Column(String(100), nullable= False)
    date_of_birth_customer = Column(Date, nullable= False)
    sexe_customer = Column(String, nullable= False)
    address_customer = Column(String)

    # Un client peut avoir plusieurs factures
    invoice = relationship("t_invoice", back_populates="customer")
   

    def __repr__(self):
       return f"Customer name : {self.name_customer} (Email : {self.email_customer})"
    

class t_product(Base):
    __tablename__ = 't_product'
    __table_args__ = ({"schema": "patricia"},) # Spécifier le schéma

    id_product = Column(Integer, primary_key=True, autoincrement=True)
    name_product = Column(String(100), nullable= False)
    unit_price = Column(DECIMAL(10,2), nullable= False)
       
    # Un produit est présent dans plusieurs lignes de factures.
    # Relation plusieurs-à-plusieurs avec t_invoices via la table d'association t_invoices_items
    invoice = relationship("t_invoice", secondary="t_invoice_item", back_populates="product")

    # relation vers t_invoices_items 
    invoice_item = relationship("t_invoices_items", back_populates="product")

    
    def __repr__(self):
       return f"Product name: {self.name_product}, Unit price: {self.unit_price}"

    

class t_invoice_item(Base):
    __tablename__ = 't_invoices_items'
    __table_args__ = (
        {"schema": "patricia"},  # Schéma spécifié ici
        #CheckConstraint('quantities > 0', name='check_quantities_positives')  # Contrainte Check
    )

    id_item = Column(Integer, primary_key=True, autoincrement=True)
    id_invoice = Column(String, ForeignKey("patricia.t_invoice.id_invoice", ondelete="CASCADE"), nullable=False)
    id_product = Column(Integer, ForeignKey("patricia.t_product.id_product", ondelete="CASCADE"), nullable=False)

    subtotals = Column(DECIMAL(10,2), nullable= False)
    quantities = Column(Integer, nullable=True)

    # Chaque ligne de facture est associée à une facture spécifique.
    # Relation avec la facture (ligne de facture associée à une facture)
    invoice = relationship("t_invoice", back_populates="invoice_item")

    # Chaque ligne de facture concerne un produit spécifique.
    # Relation avec le produit (ligne de facture associée à un produit)
    product = relationship("t_product", back_populates="invoice_item") 

    def __repr__(self):
       return f"INVOICE ITEM n°{self.id_item} (Subtotal: {self.subtotals}, Quantity: {self.quantities})"

 