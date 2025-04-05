import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, DateTime, DECIMAL, CheckConstraint, func
from sqlalchemy.orm import declarative_base, relationship
from app.db.connect_to_db import Base

# Update invoices table
class t_invoice(Base):
    __tablename__ = 't_invoice'
    __table_args__ = ({"schema": "patricia"},)

    id_invoice = Column(String, primary_key=True)
    id_customer = Column(Integer, ForeignKey("patricia.t_customer.id_customer"), nullable=False)
    name_invoice = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    modified_at = Column(DateTime, nullable=True)
    content_length = Column(Integer, nullable=True)
    content_md5 = Column(String, nullable=True)
    issue_date = Column(DateTime, nullable=True)
    total_amount = Column(DECIMAL(10, 2), nullable=True)

    customer = relationship("t_customer", back_populates="invoice")
    invoice_item = relationship("t_invoice_item", back_populates="invoice", cascade="all, delete")

    def __repr__(self):
        return f"INVOICE n°{self.id_invoice} Invoice name : {self.name_invoice})"


class t_customer(Base):
    __tablename__ = 't_customer'
    __table_args__ = ({"schema": "patricia"},)

    id_customer = Column(Integer, primary_key=True, autoincrement=True)
    email_customer = Column(String(255), unique=True, nullable=True)
    name_customer = Column(String(100), nullable=False)
    date_of_birth_customer = Column(Date, nullable=False)
    sexe_customer = Column(String, nullable=False)
    address_customer = Column(String)

    invoice = relationship("t_invoice", back_populates="customer")

    def __repr__(self):
        return f"Customer name : {self.name_customer} (Email : {self.email_customer})"


class t_product(Base):
    __tablename__ = 't_product'
    __table_args__ = ({"schema": "patricia"},)

    id_product = Column(Integer, primary_key=True, autoincrement=True)
    name_product = Column(String(100), nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)

    invoice_item = relationship("t_invoice_item", back_populates="product")

    def __repr__(self):
        return f"Product name: {self.name_product}, Unit price: {self.unit_price}"


class t_invoice_item(Base):
    __tablename__ = 't_invoice_item'
    __table_args__ = ({"schema": "patricia"},)

    id_item = Column(Integer, primary_key=True, autoincrement=True)
    id_invoice = Column(String, ForeignKey("patricia.t_invoice.id_invoice", ondelete="CASCADE"), nullable=False)
    id_product = Column(Integer, ForeignKey("patricia.t_product.id_product", ondelete="CASCADE"), nullable=False)

    subtotals = Column(DECIMAL(10, 2), nullable=True)
    quantities = Column(Integer, nullable=True)

    invoice = relationship("t_invoice", back_populates="invoice_item")
    product = relationship("t_product", back_populates="invoice_item")

    def __repr__(self):
        return f"INVOICE ITEM n°{self.id_item} (Subtotal: {self.subtotals}, Quantity: {self.quantities})"


#this is the model for the user table
# it is used for authentication and authorization purposes
from sqlalchemy import Column, Integer, String
from app.db.connect_to_db import Base

class t_user(Base):
    __tablename__ = "t_user"

    id_user = Column(Integer, primary_key=True, index=True)
    email_user = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
