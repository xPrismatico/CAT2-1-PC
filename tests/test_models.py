"""Tests unitarios para los modelos ProductType y Product de TechScout."""

import pytest

from techscout.models import Product, ProductType


def test_product_type_name_no_vacio() -> None:
    """ProductType.name no debe aceptar strings vacíos."""
    with pytest.raises(ValueError):
        ProductType(name="   ")


def test_product_type_valido() -> None:
    """ProductType se crea correctamente con un nombre válido."""
    product_type = ProductType(name="Tablets")
    assert product_type.name == "Tablets"


def test_product_id_invalido() -> None:
    """Product.product_id debe ser mayor o igual a 1."""
    with pytest.raises(ValueError):
        Product(product_id=0, title="Laptop X", price_usd=1000.0)


def test_product_price_negativo_invalido() -> None:
    """Product.price_usd no puede ser negativo."""
    with pytest.raises(ValueError):
        Product(product_id=10, title="Phone Y", price_usd=-50.0)


def test_product_title_vacio_invalido() -> None:
    """Product.title no puede estar vacío."""
    with pytest.raises(ValueError):
        Product(product_id=15, title="   ", price_usd=200.0)


def test_product_valido() -> None:
    """Product se crea correctamente con datos válidos."""
    product = Product(product_id=37, title="Asus ROG", price_usd=1281.99)
    assert product.product_id == 37
    assert product.title == "Asus ROG"
    assert product.price_usd == 1281.99
