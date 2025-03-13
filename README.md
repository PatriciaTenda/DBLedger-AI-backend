# DBLedger-AI-backend
DBLedger-AI est une application web qui optimise le prétraitement des factures via l’OCR, convertissant images et PDF en texte. Les données extraites sont traitées, stockées et exploitées par un système de reporting automatisé. Un seuil de qualité garantit la fiabilité des informations, assurant une gestion simplifiée et un suivi comptable optimisé.

Generic single-database configuration.

## Installation
## OCR_2025
Sample project OCR

## API Factures

Récupération de la liste des factures (année 2018, format XML):  
GET **CONTAINER_URL**/invoices-_2018_?restype=container&comp=list&**CONTAINER_SAS**
### Schéma XML (API liste fichiers)
```text
─ EnumerationResults
   └─Blobs
      └─Blob (*)
        ├─Name
        └─Properties
```
Récupération d'une facture (format PNG):  
GET **CONTAINER_URL**/invoices-_2018_/_FAC_2018_0014-558.png_?**CONTAINER_SAS**

```bash
 py -m venv venv
 venv/Scripts/activate
 pip install -r requirements.txt
```

### pip tools
Génère le `requirements.txt` (clean, avec librairies & version) à partir du `requirements.in`
```bash
 pip install pip-tools
 pip-compile
```

### Installation alembic

```bash

# Installer alembic
    pip install alembic

# Initialise Alembic
    alembic init migrations

# architecure du repertoire migrations/
/alembic
├── env.py          # Script de configuration d'Alembic
├── versions/       # Contient les scripts de migration générés
├── script.py.mako  # Template par défaut pour les migrations
└── alembic.ini     # Fichier de configuration de base d'Alembic à la racine 
```