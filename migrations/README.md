Generic single-database configuration.

```bash

# Installer alembic
    pip install alembic

# Initialise Alembic
    alembic init migrations

# architecure du repertoire migrations/
/migrations
├── env.py          # Script de configuration d'Alembic
├── versions/       # Contient les scripts de migration générés
├── script.py.mako  # Template par défaut pour les migrations
└── alembic.ini     # Fichier de configuration de base d'Alembic

