"""
Módulo de scraping de TechScout con Selenium

Recorre subcategorías del catálogo en webscraper.io usando Selenium headless,
extrayendo productos, limpiando precios y manejando excepciones individuales.
"""

import logging
import re
from dataclasses import dataclass
from typing import List, Optional

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

# Selectores CSS exigidos en la rúbrica
CARD_SELECTOR = ".card.thumbnail"
TITLE_SELECTOR = "a.title"
PRICE_SELECTOR = 'span[itemprop="price"]'
ACTIVE_MENU_SELECTOR = "#side-menu a.active"
DEFAULT_TIMEOUT = 10


@dataclass
class ScrapedProduct:
    """Representa un producto crudo extraído de una tarjeta del catálogo.

    Attributes:
        product_id: Identificador numérico del producto extraído de la URL.
        title: Título del producto.
        type_name: Nombre de la categoría (obtenido del menú lateral).
        price_usd: Precio del producto sin símbolo '$' y convertido a float.
    """

    product_id: int
    title: str
    type_name: str
    price_usd: float


def _build_driver(headless: bool = True) -> webdriver.Chrome:
    """Construye una instancia de Chrome WebDriver.

    Args:
        headless: Si es True, el navegador se ejecuta sin interfaz gráfica.

    Returns:
        Instancia configurada de webdriver.Chrome.
    """
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # En Selenium 4.10+, Chrome DriverManager es nativo y automático.
    return webdriver.Chrome(options=options)


def _extract_product_id(card: WebElement) -> Optional[int]:
    """Extrae el product_id numérico desde el href del enlace del producto.

    Args:
        card: Elemento WebElement correspondiente a la tarjeta (.card.thumbnail).

    Returns:
        Identificador numérico, o None si no se encuentra.
    """
    link = card.find_element(By.CSS_SELECTOR, TITLE_SELECTOR)
    href = link.get_attribute("href") or ""
    # Busca el número al final de la URL (ej. /product/37 -> 37)
    match = re.search(r"/product/(\d+)", href)
    return int(match.group(1)) if match else None


def _clean_price(raw_price: str) -> float:
    """Limpia un precio eliminando el '$' y convirtiendo a float.

    Args:
        raw_price: Texto crudo del precio (ej. "$1281.99").

    Returns:
        El precio convertido a float.
    """
    cleaned = raw_price.replace("$", "").strip()
    return float(cleaned)


def _parse_card(card: WebElement, category_name: str) -> ScrapedProduct:
    """Extrae los datos de una única tarjeta de producto.

    Args:
        card: Elemento WebElement correspondiente a la tarjeta.
        category_name: Nombre de la categoría actual.

    Returns:
        Instancia de ScrapedProduct con los datos limpios.

    Raises:
        ValueError: Si falla la extracción del ID.
        NoSuchElementException: Si falta el título o el precio en la tarjeta.
    """
    product_id = _extract_product_id(card)
    if product_id is None:
        raise ValueError("No se pudo extraer product_id del enlace.")

    title_elem = card.find_element(By.CSS_SELECTOR, TITLE_SELECTOR)
    title = title_elem.get_attribute("title") or title_elem.text.strip()

    raw_price = card.find_element(By.CSS_SELECTOR, PRICE_SELECTOR).text
    price_usd = _clean_price(raw_price)

    return ScrapedProduct(
        product_id=product_id,
        title=title,
        type_name=category_name,
        price_usd=price_usd,
    )


def scrape_subcategory(
    base_url: str, num_pages: int = 5, headless: bool = True
) -> List[ScrapedProduct]:
    """Recorre varias páginas de una subcategoría y extrae sus productos.

    Args:
        base_url: URL base de la subcategoría (ej. .../computers/laptops).
        num_pages: Cantidad de páginas a recorrer siguiendo la paginación.
        headless: Ejecutar navegador de forma invisible.

    Returns:
        Lista de productos extraídos.
    """
    driver = _build_driver(headless=headless)
    all_products: List[ScrapedProduct] = []

    try:
        for page in range(1, num_pages + 1):
            # Sigue la paginación anexando ?page=X según rúbrica
            url = base_url if page == 1 else f"{base_url}?page={page}"
            logger.info("Scrapeando página %d: %s", page, url)
            driver.get(url)

            wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

            # 1. Extraer nombre de la subcategoría desde el menú lateral
            try:
                cat_elem = wait.until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, ACTIVE_MENU_SELECTOR))
                )
                category_name = cat_elem.text.strip()
            except TimeoutException:
                logger.warning("No se detectó menú activo, omitiendo página %d.", page)
                continue

            # 2. Esperar explícitamente a las tarjetas de producto (.card.thumbnail)
            try:
                wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, CARD_SELECTOR)))
            except TimeoutException:
                logger.warning("No se encontraron tarjetas en la página %d.", page)
                continue

            cards = driver.find_elements(By.CSS_SELECTOR, CARD_SELECTOR)

            # 3. Procesar individualmente con manejo de excepciones (try/except)
            for index, card in enumerate(cards):
                try:
                    product = _parse_card(card, category_name)
                    all_products.append(product)
                except (NoSuchElementException, ValueError) as exc:
                    logger.warning("Omisión en tarjeta #%d de pág %d: %s", index, page, exc)
                    continue

    finally:
        driver.quit()

    return all_products
