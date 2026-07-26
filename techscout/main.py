"""
Punto de entrada del pipeline TechScout

Ejecuta el flujo completo: crea la BD si no existe, scrapea la subcategoría
de Laptops, persiste los productos evitando duplicados y muestra un reporte.
Se invoca mediante el comando `make run`.
"""

import logging

from techscout.db import create_db_and_tables, get_engine
from techscout.repository import ProductRepository
from techscout.scraper import scrape_subcategory

# Configuración básica de logs para monitorear el scraping
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

TARGET_URL = "https://webscraper.io/test-sites/e-commerce/static/computers/laptops"


def run() -> None:
    """Ejecuta el pipeline completo de extracción y persistencia.

    Returns:
        None
    """
    # 1. Preparar la Base de Datos
    engine = get_engine()
    create_db_and_tables(engine)
    logger.info("Base de datos SQLite y tablas inicializadas.")

    # 2. Iniciar el Scraping (5 páginas de la subcategoría Laptops)
    logger.info("Iniciando scraping de 5 páginas en %s", TARGET_URL)
    scraped_products = scrape_subcategory(base_url=TARGET_URL, num_pages=5, headless=True)
    logger.info("Se extrajeron %d productos limpios de la web.", len(scraped_products))

    # 3. Persistir en Base de Datos (Repositorio)
    repository = ProductRepository(engine)
    repository.upsert_products(scraped_products)
    logger.info("Productos persistidos sin duplicados en la base de datos.")

    # 4. Consultas de demostración
    top_products = repository.get_top_n(5)
    logger.info("--- Top 5 Laptops más caras ---")
    for product in top_products:
        cat_name = product.type.name if product.type else "Desconocida"
        logger.info(" - [%s] %s: $%.2f", cat_name, product.title, product.price_usd)

    laptops = repository.get_products_by_type("Laptops")
    logger.info("Total de Laptops almacenadas en BD: %d", len(laptops))


if __name__ == "__main__":
    run()
