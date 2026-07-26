"""
Capa de persistencia del proyecto TechScout

Define ProductRepository, encargado de insertar y consultar productos y
tipos de producto evitando duplicados y manteniendo relaciones de tablas
"""

from typing import List, Sequence

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from techscout.models import Product, ProductType
from techscout.scraper import ScrapedProduct


class ProductRepository:
    """
    Repositorio de acceso a datos para productos y tipos de producto.

    Attributes:
        engine: Motor de base de datos usado para abrir sesiones.
    """

    def __init__(self, engine: Engine) -> None:
        """
        Inicializa el repositorio con un motor de base de datos ya creado.

        Args:
            engine: Instancia de Engine obtenida vía get_engine().

        Returns:
            None
        """
        self.engine = engine

    def get_or_create_type(self, name: str) -> ProductType:
        """
        Busca un ProductType por nombre, creándolo si no existe.

        Args:
            name: Nombre del tipo de producto a buscar o crear.

        Returns:
            La instancia (existente o recién creada) de ProductType.
        """
        with Session(self.engine) as session:
            statement = select(ProductType).where(ProductType.name == name)
            existing = session.exec(statement).first()
            if existing is not None:
                return existing

            product_type = ProductType(name=name)
            session.add(product_type)
            session.commit()
            session.refresh(product_type)
            return product_type

    def upsert_products(self, scraped_products: Sequence[ScrapedProduct]) -> None:
        """
        Inserta productos nuevos y omite los que ya existen por product_id.

        Cada producto queda enlazado a su ProductType correspondiente,
        creando el tipo si aún no existe en la base de datos.

        Args:
            scraped_products: Secuencia de productos crudos del scraper.

        Returns:
            None
        """
        with Session(self.engine) as session:
            for item in scraped_products:
                # 1. Resolver el ProductType
                type_stmt = select(ProductType).where(ProductType.name == item.type_name)
                product_type = session.exec(type_stmt).first()

                if product_type is None:
                    product_type = ProductType(name=item.type_name)
                    session.add(product_type)
                    session.flush()  # Obtiene el ID sin cerrar transacción

                # 2. Verificar duplicado por product_id
                prod_stmt = select(Product).where(Product.product_id == item.product_id)
                existing = session.exec(prod_stmt).first()

                if existing is not None:
                    continue  # Si existe, lo omitimos (evita duplicados)

                # 3. Crear el nuevo producto
                product = Product(
                    product_id=item.product_id,
                    title=item.title,
                    price_usd=item.price_usd,
                    type_id=product_type.id,
                )
                session.add(product)

            # Commit final de toda la transacción
            session.commit()

    def get_top_n(self, n: int) -> List[Product]:
        """
        Obtiene los N productos más caros, con su tipo ya cargado.

        Args:
            n: Cantidad de productos a retornar.

        Returns:
            Lista de los productos con mayor price_usd, ordenados. El nombre
            del tipo es accesible vía product.type.name gracias a la relación.
        """
        with Session(self.engine) as session:
            statement = select(Product).order_by(Product.price_usd.desc()).limit(n)
            products = session.exec(statement).all()

            # Forzamos la carga de la relación para evitar DetachedInstanceError
            for product in products:
                _ = product.type.name if product.type else None

            return list(products)

    def get_products_by_type(self, type_name: str) -> List[Product]:
        """
        Obtiene todos los productos que pertenecen a un tipo dado.

        Args:
            type_name: Nombre del ProductType a filtrar.

        Returns:
            Lista de productos asociados a ese tipo. Vacía si no existe.
        """
        with Session(self.engine) as session:
            statement = select(ProductType).where(ProductType.name == type_name)
            product_type = session.exec(statement).first()

            if product_type is None:
                return []

            # Acceso mediante la relación 'products' configurada en el modelo
            return list(product_type.products)
