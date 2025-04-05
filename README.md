# DBLedger-AI-backend
DBLedger-AI est une application web qui optimise le prétraitement des factures via l’OCR, convertissant images et PDF en texte. Les données extraites sont traitées, stockées et exploitées par un système de reporting automatisé. Un seuil de qualité garantit la fiabilité des informations, assurant une gestion simplifiée et un suivi comptable optimisé.

Generic single-database configuration.

## Installation

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
## Configuration base de données
### Instalation SQLAlchimy

```bash 
    pip install SQLAlchymi
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

## Installation OCR et openCV

```bash
    pip install pytesseract
    pip install opencv-python
```

## Installation de pyzbar pour décoder le QRcode 

```bash
    pip install pyzbar

```

### Pour resoudre le l'erreur  libzbar-64.dll not found
 Il faut téléchargé le fichier vc_redist.x64.exe
 le lien officiel de Microsoft :
🔗 https://learn.microsoft.com/fr-fr/cpp/windows/latest-supported-vc-redist



## Installation de la librairie python-multipart
```bash
    pip install python-multipart
```


## Mise en place du système d'authentification des utilisateurs

### Authentification & Sécurité
Le système d'authentification de DBLedger-AI repose sur un mécanisme simple et sécurisé utilisant :

🔑 Formulaire de connexion (email + mot de passe)

🔒 Hachage des mots de passe avec bcrypt

🔁 Vérification du mot de passe lors de la connexion

🔄 Redirection en cas d’échec ou de succès

✅ Gestion des erreurs utilisateur avec feedback visuel (Toast Bootstrap)

#### Fonctionnement
Création d’un utilisateur (à faire via Alembic ou script Python)

Les mots de passe sont hachés avant d’être stockés en base.

Utilisation de la fonction hash_password(password).

##### Connexion

Le formulaire /login envoie les données à la route /auth/jwt/login.

Vérification de l’email et du mot de passe via la fonction verify_password(...).

En cas de succès : redirection vers /upload_invoice.

En cas d’échec : redirection vers /login?error=invalid avec affichage d’un message d'erreur via un toast.

##### Sécurité

Aucune information sensible n’est stockée en clair.

Le système est conçu pour une authentification simple avant extension future vers OAuth2 / JWT.

 Compte test (exemple)

```bash
    Email : admin@example.com
    Mot de passe : secret
```
Ce compte est utilisé à des fins de démonstration (dans la version de développement).

#### Ajouter un utilitaire de hash de mot de passe
##### Installation de bcrypt
bcrypt : un algorithme sécurisé recommandé pour le stockage de mots de passe.
```bash
    pip install bcrypt
```

##### Installation passlib
passlib : pour le hashage et la vérification des mots de passe.
```bash
   pip install passlib[bcrypt]
```
#### Installion module itsdangerous
La session dans Starlette/FastAPI utilise itsdangerous pour signer les données de session.
```bash
    pip install itsdangerous
```
