"""Utilidades de conexión y creación del esquema de base de datos TechScout"""

from pathlib import Path

from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, create_engine

from techscout.models import Product, ProductType  # noqa: F401

DEFAULT_DB_PATH = Path("data/processed/techscout.db")


def get_engine(db_path: Path = DEFAULT_DB_PATH) -> Engine:
    """
    Construye y retorna el motor de base de datos SQLite.

    Crea los directorios necesarios si no existen.

    Args:
        db_path: Ruta al archivo local de SQLite.

    Returns:
        Motor de conexión (Engine) configurado.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    sqlite_url = f"sqlite:///{db_path}"
    return create_engine(sqlite_url, echo=False)


def create_db_and_tables(engine: Engine) -> None:
    """
    Crea todas las tablas definidas en SQLModel.metadata.

    Args:
        engine: Motor de base de datos sobre el que se ejecutarán las tablas.

    Returns:
        None
    """
    SQLModel.metadata.create_all(engine)
