# DBLedger-AI – Backend
DBLedger-AI est une solution intelligente de traitement de factures, conçue pour extraire automatiquement les informations à partir de fichiers images ou PDF à l’aide de l’OCR et des QR codes, stocker ces données de façon structurée dans une base de données, puis les exploiter à travers un système de reporting dynamique et des analyses client/produit.

# Structure du projet
```bash
DBLedger-AI-BACKEND/
├── app/
│   ├── auth/                # Authentification utilisateur (hash, login, sécurité)
│   ├── db/                  # Modèles de base de données et accès CRUD
│   ├── ocr_services/        # Services d’OCR & traitement de facture
├── data_images/             # Dossier de stockage des factures à traiter
├── exports/                 # Fichiers exportés (CSV, résultats de reporting)
├── logs/                    # Logs du système
├── migrations/              # Scripts Alembic pour les migrations SQLAlchemy
├── notebook/                # Notebooks EDA et Machine Learning
├── static/                  # Fichiers statiques (CSS, JS, images)
├── templates/               # Templates HTML pour l’interface web
├── test/                    # Tests unitaires et fonctionnels
├── venv/                    # Environnement virtuel
├── extracted_invoice.json   # Exemple de résultat d’extraction OCR
├── resultat_pretraite.png   # Résultat visuel de l’OCR/QR
├── main.py                  # Fichier principal FastAPI (routes & logique)
├── requirements.in          # Dépendances (version souple)
├── requirements.txt         # Dépendances (version figée)
├── .env                     # Variables d’environnement
├── alembic.ini              # Config Alembic
├── Dockerfile               # Conteneurisation
├── docker-compose.yml       # Orchestration du backend
└── README.md                # Documentation du projet

```
# Fonctionnalités
- OCR & QR code pour extraire automatiquement les données de factures

- Classification automatique & segmentation client RFM

- Stockage structuré dans PostgreSQL via SQLAlchemy

- Dashboards interactifs (ventes, CA, clients)

- Authentification utilisateur sécurisée

- Notebooks d’analyse de données et d'entraînement de modèles ML

- API REST + interface HTML via FastAPI + Jinja2

# Installation
1. Cloner le dépôt et créer l'environnement
```bash

git clone https://github.com/ton-compte/DBLedger-AI-backend.git
cd DBLedger-AI-backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows
```
2. Installer les dépendances

```bash
pip install -r requirements.txt
```
3. Configuration base de données (SQLAlchemy + Alembic)
```bash
pip install sqlalchemy alembic psycopg2-binary
alembic init migrations
```
# Traitement OCR & QR code
## Installation des librairies nécessaires
```bash
pip install pytesseract opencv-python pyzbar
```
En cas d'erreur libzbar-64.dll
Télécharger le redistribuable Visual C++ :
🔗 Lien Microsoft

# Authentification utilisateur
Mécanisme basé sur bcrypt, passlib, et itsdangerous :

```bash
pip install bcrypt passlib[bcrypt] python-multipart itsdangerous
```

## Fonctionnalités :

- Hachage des mots de passe

- Formulaire de connexion

- Redirection dynamique

- Feedback utilisateur

# Reporting & Visualisation
## Tableaux HTML interactifs avec Bootstrap

- Tri, recherche, export CSV

- Graphique RFM (matplotlib)

- Chiffre d’affaires par an, top produits

- Monitoring visuel

# Notebooks d’analyse
Dans le dossier notebook, tu trouveras :

- Analyse exploratoire (clients & produits)

- Préparation des données pour la segmentation RFM

# Tests d'algorithmes ML simples
```bash
```

# Installation des librairies pour notebook
```bash
pip install ipykernel pandas matplotlib scikit-learn sqlalchemy
python -m ipykernel install --user --name=dbledger-kernel --display-name "Python (DBLedger-AI)"
```
# Dockerisation 
Lancement avec Docker Compose
```bash
docker-compose up --build
```
# À venir

- Ajout de filtres intelligents par segment client

- Dashboard client avec alertes personnalisées

- Docker
  
- Déploiement sur plateforme cloud (Render, Railway ou autre)


# Contributeurs
Projet réalisé dans le cadre d’une formation IA par Patricia TENDA
Créé pour explorer la mise en œuvre concrète d’un backend OCR intelligent avec dashboards dynamiques et sécurité intégrée.
