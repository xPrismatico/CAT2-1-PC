"""
Modelos de datos del proyecto TechScout.

Define las entidades persistentes ProductType y Product utilizando SQLModel,
con relaciones bidireccionales y validaciones requeridas.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import validates
from sqlmodel import Field, Relationship, SQLModel


class ProductType(SQLModel, table=True):
    """
    Categoría o subcategoría de producto.

    Attributes:
        id: Identificador primario en la base de datos.
        name: Nombre único de la categoría.
        products: Relación bidireccional hacia los productos.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False)

    products: List["Product"] = Relationship(back_populates="type")

    @validates("name")
    def name_no_vacio(self, key: str, value: str) -> str:
        """
        Valida que el nombre de la categoría no esté vacío.

        Args:
            key: Nombre del atributo (name).
            value: Valor propuesto para la categoría.

        Returns:
            El nombre validado sin espacios en los extremos.

        Raises:
            ValueError: Si el string está vacío o solo contiene espacios.
        """
        if not value or not value.strip():
            raise ValueError("El nombre de ProductType no puede estar vacío.")
        return value.strip()


class Product(SQLModel, table=True):
    """Producto individual extraído del catálogo web.

    Attributes:
        id: Identificador interno autogenerado.
        product_id: ID único proveniente de la URL del producto.
        title: Título o nombre del producto.
        price_usd: Precio numérico en dólares.
        scraped_at: Marca de tiempo de cuando fue extraído.
        type_id: Llave foránea hacia ProductType.
        type: Objeto ProductType asociado vía la relación.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(ge=1, index=True, unique=True, nullable=False)
    title: str = Field(nullable=False)
    price_usd: float = Field(ge=0.0, nullable=False)
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    type_id: Optional[int] = Field(default=None, foreign_key="producttype.id")

    type: Optional[ProductType] = Relationship(back_populates="products")

    @validates("product_id")
    def product_id_valido(self, key: str, value: int) -> int:
        """
        Valida que el ID del producto sea válido (>= 1).

        Args:
            key: Nombre del atributo (product_id).
            value: Valor numérico propuesto.

        Returns:
            El ID validado si cumple la condición.

        Raises:
            ValueError: Si el valor es menor a 1.
        """
        if value < 1:
            raise ValueError("product_id debe ser mayor o igual a 1.")
        return value

    @validates("price_usd")
    def price_usd_valido(self, key: str, value: float) -> float:
        """
        Valida que el precio del producto no sea negativo.

        Args:
            key: Nombre del atributo (price_usd).
            value: Precio propuesto.

        Returns:
            El precio validado.

        Raises:
            ValueError: Si el precio es menor a 0.
        """
        if value < 0:
            raise ValueError("price_usd debe ser mayor o igual a 0.")
        return value

    @validates("title")
    def title_no_vacio(self, key: str, value: str) -> str:
        """
        Valida que el título del producto no esté vacío.

        Args:
            key: Nombre del atributo (title).
            value: Título propuesto.

        Returns:
            El título validado sin espacios extra.

        Raises:
            ValueError: Si el string está vacío o contiene solo espacios.
        """
        if not value or not value.strip():
            raise ValueError("El título del producto no puede estar vacío.")
        return value.strip()
