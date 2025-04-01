from fastapi import FastAPI, Request, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, shutil
from fastapi import Request
from datetime import datetime
from app.ocr_services.ocr_pipeline_runner import run_ocr_pipeline
from app.db.models import t_product, t_invoice_item
from sqlalchemy.orm import joinedload, func


from app.db.connect_to_db import Session
from app.db.crud import get_or_create_customer
import app.db.models

app = FastAPI()
#  Pour retrouver le bon chemin
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


#  Montre les fichiers statiques (CSS, JS...)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

#  Chemin vers les templates HTML
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/upload_invoice", response_class=HTMLResponse)
async def upload_invoice_page(request: Request):
    return templates.TemplateResponse("upload_invoice.html", {"request": request})

@app.get("/new-customer", response_class=HTMLResponse)
async def new_customer_form(request: Request):
    return templates.TemplateResponse("save_customer.html", {"request": request})

@app.get("/ocr_extract", response_class=HTMLResponse)
async def ocr_extract(request: Request):
    return templates.TemplateResponse("ocr_extracted.html", {"request": request, })

@app.get("/logout", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/d-list", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("d-list.html", {"request": request})

@app.post("/fetch-invoice-data", response_class=HTMLResponse)
async def upload(request: Request, file: UploadFile = File(...)):
    file_location = os.path.join(BASE_DIR, "data_images/images_for_extraction", file.filename)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_data = run_ocr_pipeline(file_location)

    return templates.TemplateResponse("ocr_extracted.html", {
        "request": request,
        "extracted_data": extracted_data
    })

#cette route est pour le formulaire de création de client

@app.post("/save-customer", response_class=HTMLResponse)
async def save_customer(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    gender: str = Form(...),
    birthdate: str = Form(...)
):
    db_session = Session()

    customer_data = {
        "name": name,
        "email": email,
        "address": address,
        "gender": gender,
        "birthdate": datetime.strptime(birthdate, "%Y-%m-%d")
    }

    # Création ou récupération du client
    customer = get_or_create_customer(db_session, email=email, data=customer_data)

    print(customer)  # Debug : Affiche l’objet customer dans la console

    return templates.TemplateResponse("success.html", {
        "request": request,
        "customer_name": customer.name_customer
    })


@app.get("/product-report", response_class=HTMLResponse)
def product_report(request: Request):
    db = Session()
    
    # Requête pour regrouper les données produits
    result = (
        db.query(
            t_product.name_product,
            func.sum(t_invoice_item.quantities).label("total_quantity"),
            func.sum(t_invoice_item.subtotals).label("total_revenue")
        )
        .join(t_invoice_item, t_product.id_product == t_invoice_item.id_product)
        .group_by(t_product.name_product)
        .all()
    )
    
    db.close()
    return templates.TemplateResponse("report_products.html", {"request": request, "products": result})