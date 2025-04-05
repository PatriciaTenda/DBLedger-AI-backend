from fastapi import FastAPI, Request, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime , date
from dotenv import load_dotenv
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE
from io import StringIO
from fastapi.responses import StreamingResponse
from operator import itemgetter
from collections import Counter

from app.ocr_services.ocr_pipeline_runner import run_ocr_pipeline
from app.db.models import t_product, t_invoice_item, t_invoice, t_customer, t_user
from app.auth.scurity import hash_password, verify_password
from sqlalchemy import func, extract, desc
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload
from app.db.connect_to_db import Session
from app.db.crud import get_or_create_customer

import os, shutil, secrets, csv, pandas as pd, json

# Charger variables d'environnement depuis .env
load_dotenv()
secret_key = os.getenv("SECRET_KEY")

# Initialisation de l'application FastAPI
app = FastAPI()

# Middleware pour les sessions utilisateur (stocké dans les cookies)
app.add_middleware(SessionMiddleware, secret_key="secret-key")

# Configuration des répertoires
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/invoice/image", StaticFiles(directory="data_images/data_extraction_ignored"), name="extracted_images")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ----------------------------- AUTHENTIFICATION -----------------------------
@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/upload_invoice", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/auth/jwt/login", tags=["Authentication"])
async def login_check(request: Request, username: str = Form(...), password: str = Form(...)):
    db = Session()
    user = db.query(t_user).filter(t_user.email_user == username).first()
    if not user or not verify_password(password, user.password_hash):
        request.session.clear()
        return RedirectResponse(url="/login?error=invalid", status_code=302)
    request.session["user"] = user.email_user
    return RedirectResponse(url="/upload_invoice", status_code=302)

@app.get("/signup", response_class=HTMLResponse, tags=["Authentication"])
async def show_signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup", response_class=HTMLResponse, tags=["Authentication"])
async def register_user(request: Request, email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    db = Session()
    error = None
    try:
        if password != confirm_password:
            error = "Passwords do not match"
        elif db.query(t_user).filter_by(email_user=email).first():
            error = "Email already in use"
        if error:
            return templates.TemplateResponse("signup.html", {"request": request, "error": error})
        hashed_pw = hash_password(password)
        new_user = t_user(email_user=email, password_hash=hashed_pw)
        db.add(new_user)
        db.commit()
        return templates.TemplateResponse("signup_success.html", {"request": request, "user_email": email})
    finally:
        db.close()

@app.get("/logout", tags=["Authentication"])
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

# ----------------------------- PAGES PUBLIQUES -----------------------------
@app.get("/", response_class=HTMLResponse, tags=["Pages"])
async def landing_page(request: Request):
    return templates.TemplateResponse("landing_page.html", {"request": request})

# ----------------------------- INVOICES (OCR) -----------------------------
@app.get("/upload_invoice", response_class=HTMLResponse, tags=["Invoices"])
async def upload_invoice_page(request: Request):
    return templates.TemplateResponse("upload_invoice.html", {"request": request, "extracted_data": {}})

@app.post("/fetch-invoice-data", response_class=HTMLResponse, tags=["Invoices"])
async def upload(request: Request, file: UploadFile = File(...)):
    file_location = os.path.join(BASE_DIR, "data_images/data_extraction_ignored", file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    extracted_data = run_ocr_pipeline(file_location)
    return templates.TemplateResponse("ocr_extracted.html", {"request": request, "extracted_data": extracted_data})

@app.get("/invoice", response_class=HTMLResponse, tags=["Invoices"])
def invoice(request: Request, selected: str = None):
    data_dir = Path("data_images/data_extraction_ignored")
    image_files = [
        {"name": f.name, "url": f"/data_images/data_extraction_ignored/{f.name}"}
        for f in data_dir.glob("*")
        if f.suffix.lower() in [".png", ".jpg", ".jpeg", ".pdf"]
    ]
    selected_image = f"/invoice/image/{selected}" if selected else None
    return templates.TemplateResponse("fetch_invoice.html", {"request": request, "invoices": image_files, "selected": selected, "selected_image": selected_image})

@app.get("/ocr_extract", response_class=HTMLResponse, tags=["Invoices"])
async def ocr_extract(request: Request):
    return templates.TemplateResponse("ocr_extracted.html", {"request": request})

# ----------------------------- CUSTOMERS -----------------------------
@app.get("/new-customer", response_class=HTMLResponse, tags=["Customers"])
async def new_customer_form(request: Request):
    return templates.TemplateResponse("save_customer.html", {"request": request})

@app.post("/save-customer", response_class=HTMLResponse, tags=["Customers"])
async def save_customer(request: Request, name: str = Form(...), email: str = Form(...), address: str = Form(...), gender: str = Form(...), birthdate: str = Form(...)):
    db_session = Session()
    customer_data = {
        "name": name,
        "email": email,
        "address": address,
        "gender": gender,
        "birthdate": datetime.strptime(birthdate, "%Y-%m-%d")
    }
    customer = get_or_create_customer(db_session, email=email, data=customer_data)
    return templates.TemplateResponse("save_cust_success.html", {"request": request, "customer_name": customer.name_customer})

# ----------------------------- REPORTS -----------------------------
@app.get("/product-report", response_class=HTMLResponse, tags=["Reports"])
def product_report(request: Request):
    try:
        db = Session()
        result = db.query(
            t_product.name_product,
            func.sum(t_invoice_item.quantities).label("total_quantity"),
            func.sum(t_invoice_item.subtotals).label("total_revenue")
        ).join(t_invoice_item, t_product.id_product == t_invoice_item.id_product)
        result = result.group_by(t_product.name_product).all()
        total_quantity = sum([r.total_quantity or 0 for r in result])
        total_revenue = sum([r.total_revenue or 0 for r in result])

        revenue_by_year_query = db.query(
            extract('year', t_invoice.issue_date).label("year"),
            func.sum(t_invoice_item.subtotals).label("revenue")
        ).join(t_invoice, t_invoice_item.id_invoice == t_invoice.id_invoice)
        revenue_by_year_query = revenue_by_year_query.group_by(extract('year', t_invoice.issue_date)).order_by("year").all()

        revenue_by_year = [{"year": int(r.year), "revenue": float(r.revenue)} for r in revenue_by_year_query]

        top_products_query = db.query(
            t_product.name_product.label("name"),
            func.sum(t_invoice_item.subtotals).label("revenue")
        ).join(t_invoice_item, t_product.id_product == t_invoice_item.id_product)
        top_products_query = top_products_query.group_by(t_product.name_product).order_by(func.sum(t_invoice_item.subtotals).desc()).limit(5).all()

        top_products = [{"name": r.name, "revenue": float(r.revenue)} for r in top_products_query]
        product_reports = []

        products = db.query(t_product).all()
        for p in products:
            sales = db.query(
                t_invoice.id_invoice,
                t_invoice.issue_date,
                t_invoice_item.quantities,
                t_invoice_item.subtotals
            ).join(t_invoice, t_invoice.id_invoice == t_invoice_item.id_invoice).filter(t_invoice_item.id_product == p.id_product).all()
            if sales:
                product_reports.append({"product": p, "sales": sales})

        return templates.TemplateResponse("report_products.html", {
            "request": request,
            "products": result,
            "total_quantity": total_quantity,
            "total_revenue": total_revenue,
            "revenue_by_year": revenue_by_year,
            "top_products": top_products,
            "product_reports": product_reports
        })
    except OperationalError:
        raise HTTPException(status_code=503, detail="Connexion à la base impossible.")
    finally:
        db.close()

@app.get("/export-product-report", tags=["Reports"])
def export_product_report():
    db = Session()
    try:
        result = db.query(
            t_product.name_product,
            func.sum(t_invoice_item.quantities).label("total_quantity"),
            func.sum(t_invoice_item.subtotals).label("total_revenue")
        ).join(t_invoice_item, t_product.id_product == t_invoice_item.id_product)
        result = result.group_by(t_product.name_product).all()

        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)
        file_path = os.path.join(export_dir, "product_report.csv")

        with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Product", "Total Quantity Sold", "Total Revenue (€)"])
            for r in result:
                writer.writerow([r.name_product, r.total_quantity, f"{r.total_revenue:.2f}"])

        return FileResponse(path=file_path, filename="product_report.csv", media_type="text/csv")
    finally:
        db.close()

# ----------------------------- CUSTOMER REPORT -----------------------------
@app.get("/customer-report", response_class=HTMLResponse, tags=["Reports"])
def customer_report(request: Request):
    try:
        db = Session()  # ou Session() si tu n'as pas SessionLocal

        result = db.query(
            t_customer.id_customer,
            t_customer.name_customer,
            t_customer.email_customer,
            func.count(t_invoice.id_invoice).label("total_invoices"),
            func.sum(t_invoice.total_amount).label("total_amount"),
            func.avg(t_invoice.total_amount).label("avg_amount"),
            func.max(t_invoice.issue_date).label("last_invoice_date")
        ).join(t_invoice, t_invoice.id_customer == t_customer.id_customer)\
         .group_by(t_customer.id_customer)\
         .order_by(desc("total_amount"))\
         .all()

        total_clients = len(result)
        total_revenue_all_clients = sum([r.total_amount or 0 for r in result])

        # Top clients (les 5 meilleurs en CA)
        top_clients = sorted(result, key=lambda x: x.total_amount or 0, reverse=True)[:5]
        chart_data = {
            "labels": [c.name_customer for c in top_clients],
            "revenues": [float(c.total_amount or 0) for c in top_clients],
            "invoices": [int(c.total_invoices or 0) for c in top_clients],
        }
            

        return templates.TemplateResponse("customer_report.html", {
            "request": request,
            "report": result,
            "total_clients": total_clients,
            "total_revenue_all_clients": total_revenue_all_clients,
            "chart_data": json.dumps(chart_data)
        })

    except OperationalError:
        raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail="Connexion à la base de données impossible.")
    finally:
        db.close()

# Exporter le rapport client au format CSV
@app.get("/export-customer-report", tags=["Reports"])
def export_customer_report():
    try:
        db = Session()

        result = db.query(
            t_customer.name_customer,
            t_customer.email_customer,
            func.count(t_invoice.id_invoice).label("total_invoices"),
            func.sum(t_invoice.total_amount).label("total_amount"),
            func.avg(t_invoice.total_amount).label("avg_amount"),
            func.max(t_invoice.issue_date).label("last_invoice_date")
        ).join(t_invoice, t_invoice.id_customer == t_customer.id_customer)\
         .group_by(t_customer.id_customer)\
         .order_by(desc("total_amount"))\
         .all()


     # Créer le dossier exports/ s'il n'existe pas
        os.makedirs("exports", exist_ok=True)

        # Nom dynamique avec date/heure
        filename = f"exports/customer_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Nom", "Email", "Nombre de factures", "Total Achats (€)", "Panier Moyen (€)", "Dernière Facture"])
            for row in result:
                writer.writerow([
                    row.name_customer,
                    row.email_customer,
                    row.total_invoices,
                    f"{row.total_amount or 0:.2f}",
                    f"{row.avg_amount or 0:.2f}",
                    row.last_invoice_date.strftime('%d/%m/%Y') if row.last_invoice_date else "N/A"
                ])

        return FileResponse(filename, media_type="text/csv", filename=os.path.basename(filename))

    except OperationalError:
        raise HTTPException(status_code=503, detail="Erreur base de données.")
    finally:
        db.close()

# ----------------------------- CUSTOMER SEGMENTATION -----------------------------
@app.get("/customer-segmentation", response_class=HTMLResponse, tags=["Segmentation"])
def customer_segmentation(request: Request):
    try:
        db = Session()
        today = date.today()

        result = db.query(
            t_customer.id_customer,
            t_customer.name_customer,
            t_customer.email_customer,
            func.max(t_invoice.issue_date).label("last_invoice_date"),
            func.count(t_invoice.id_invoice).label("frequency"),
            func.sum(t_invoice.total_amount).label("monetary")
        ).join(t_invoice, t_invoice.id_customer == t_customer.id_customer)\
         .group_by(t_customer.id_customer)\
         .all()

        customers_rfm = []
        for c in result:
            recency = (today - c.last_invoice_date.date()).days if c.last_invoice_date else 999
            frequency = c.frequency
            monetary = float(c.monetary or 0)
            customers_rfm.append({
                "id": c.id_customer,
                "name": c.name_customer,
                "email": c.email_customer,
                "recency": recency,
                "frequency": frequency,
                "monetary": monetary
            })

        # Fonction pour calculer les scores par quantiles
        def score(values, reverse=False):
            sorted_vals = sorted(values, reverse=reverse)
            quantiles = [sorted_vals[int(len(sorted_vals) * q / 5)] for q in range(1, 5)]
            def get_score(val):
                if val <= quantiles[0]: return 1
                elif val <= quantiles[1]: return 2
                elif val <= quantiles[2]: return 3
                elif val <= quantiles[3]: return 4
                else: return 5
            return get_score

        recency_scores = score([c["recency"] for c in customers_rfm], reverse=False)
        frequency_scores = score([c["frequency"] for c in customers_rfm], reverse=True)
        monetary_scores = score([c["monetary"] for c in customers_rfm], reverse=True)

        # 🔥 Nouvelle fonction : segment selon les scores
        def get_segment(r, f, m):
            if r >= 4 and f >= 4 and m >= 4:
                return "Champions"
            elif r >= 4 and f <= 2:
                return "New Customer"
            elif f >= 4:
                return "Loyal"
            elif r >= 3 and f >= 2 and m <= 2:
                return "Potential Loyalist"
            elif r <= 2 and f >= 3:
                return "At Risk"
            elif r == 1 and f == 1 and m == 1:
                return "Lost"
            else:
                return "Regular"

        for c in customers_rfm:
            c["r_score"] = recency_scores(c["recency"])
            c["f_score"] = frequency_scores(c["frequency"])
            c["m_score"] = monetary_scores(c["monetary"])
            c["rfm_code"] = f"{c['r_score']}{c['f_score']}{c['m_score']}"
            c["segment"] = get_segment(c["r_score"], c["f_score"], c["m_score"])

        segment_counts = Counter(c["segment"] for c in customers_rfm)
        segment_data = dict(segment_counts)

        return templates.TemplateResponse("customer_segmentation.html", {
            "request": request,
            "customers": customers_rfm,
            "segment_data": segment_data
        })

    finally:
        db.close()
