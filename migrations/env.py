import sys, os
# Ajout du repertoire parent app à sys.path avant l'importation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from dotenv import load_dotenv
from alembic import context
from alembic.config import Config
import os
from app.db.connect_to_db import Base
from app.db.models import t_invoice, t_customer, t_product, t_invoice_item, t_user

load_dotenv()  # Charge les variables depuis le fichier .env

HOST = os.getenv("HOST")
USER = os.getenv("USER")
DATABASE = os.getenv("DATABASE")
PASSWORD = os.getenv("PASSWORD")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# here we allow ourselves to pass interpolation vars to alembic.ini
# fron the host env

config.set_main_option("sqlalchemy.url", os.getenv('POSTGRES_URL').replace('%', '%%'))


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None: 
    fileConfig(config.config_file_name)


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata
include_schemas = True  # Activer la gestion des schémas

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    # Fonction pour filtrer les objets à inclure dans les migrations
    def include_object(object, name, type_, reflected, compare_to):
        if type_ == "table" and object.schema != 'patricia':
            return False
        return True
    
    # Configurer Alembic avec le filtre pour inclure uniquement certaines tables
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
            version_table_schema='patricia', # IMPORTANT !
            include_schemas=True, # Important
            include_object=include_object,  # Appliquer le filtre
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
