# 🛒 TechScout - Data Pipeline

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

**Evaluación Aplicada 1 - Programación Científica (2026)**  
**Universidad Católica del Norte, Antofagasta, Chile**  
**Autor:** Samuel Fuentes

Pipeline de datos que extrae el catálogo de productos (enfocado en subcategorías como Laptops) publicado en el sitio de práctica [Web Scraper Test Sites - E-commerce](https://webscraper.io/test-sites/e-commerce/static), los almacena en una base de datos local SQLite y deja la estructura lista para un análisis de datos posterior.

---

## 🚀 Características Principales

*   **Scraping Automatizado y Resiliente:** Extracción de datos paginados utilizando **Selenium WebDriver** en modo *headless*. Implementa esperas explícitas (`WebDriverWait`) y selectores precisos (`.card.thumbnail`), manejando excepciones tarjeta por tarjeta para no detener el flujo.
*   **Persistencia Relacional:** Modelado de datos robusto utilizando **SQLModel**. Combina el poder transaccional de *SQLAlchemy* con las validaciones estrictas de *Pydantic* (precios $\ge 0$, IDs $\ge 1$, y validación de strings vacíos).
*   **Patrón Repositorio:** Gestión de base de datos a través de una capa de persistencia (`ProductRepository`) que evita la inserción de duplicados (*upsert*) y realiza consultas relacionales navegables sin escribir *SQL crudo*.
*   **Calidad de Código y Pruebas:** Estructurado bajo el estándar modular *Cookiecutter Data Science* con **lint flake8 y format black**. El código cumple al 100% con **PEP 8**, posee *type hints* estrictos, *docstrings* en formato Google, y está protegido por pruebas unitarias usando **Pytest**.

---

## 🛠️ Requisitos Previos

*   [Conda](https://docs.conda.io/en/latest/miniconda.html) (Se recomienda Miniconda).
*   Google Chrome o Chromium instalado en el sistema (requerido para el motor de Selenium).

---

## ⚙️ Instalación y Ejecución (Guía de Revisión)

El proyecto incluye un `Makefile` para facilitar la configuración, ejecución y evaluación. Por favor, ejecute los siguientes comandos en orden desde la raíz del proyecto:

### 1. Preparar el entorno virtual
Instala todas las dependencias exactas (`sqlmodel`, `selenium`, `pytest`, `black`, `flake8`) y active el entorno aislado:

```bash
make install
conda activate techscout
```

### 2. Validar Calidad del código y Pruebas

Verifique que el código cumple con el límite de 100 caracteres, no tiene errores de sintaxis y que las validaciones de la base de datos funcionan correctamente:

```bash
# Formateo automático de código
make format

# Verificación estricta de estilo (0 errores/advertencias garantizados)
make lint

# Ejecución de la batería de pruebas unitarias
make test
```

### 3. Ejecutar el Pipeline (Scraping y Persistencia de datos)

Levanta el motor de Selenium, extrae las 5 primeras páginas de la categoría "Laptops", limpia los precios (removiendo el símbolo $), guarda todo en la base de datos techscout.db sin duplicar información y muestra por consola los productos más caros:

```bash
make run
```

## Estructura del proyecto
```plaintext
techscout_pipeline/
├── data/
│   ├── processed/          <- Directorio donde se genera y almacena la base de datos (techscout.db).
│   └── raw/                <- Datos crudos u originales.
│
├── techscout/              <- Código fuente principal del pipeline.
│   ├── __init__.py         <- Convierte el directorio en un módulo Python.
│   ├── db.py               <- Utilidades para inicializar el Engine y la BD SQLite.
│   ├── main.py             <- Punto de entrada que orquesta el scraper y la base de datos.
│   ├── models.py           <- Modelos de datos y validaciones (Product, ProductType).
│   ├── repository.py       <- Capa de persistencia (upserts y consultas relacionales).
│   └── scraper.py          <- Lógica de extracción web con Selenium WebDriver.
│
├── tests/                  <- Batería de pruebas unitarias automatizadas.
│   ├── __init__.py
│   ├── test_models.py      <- Validaciones de los modelos de SQLModel.
│   └── test_repository.py  <- Validaciones de inserción y consultas en base de datos temporal.
│
├── environment.yml         <- Definición del entorno Conda y sus dependencias.
├── Makefile                <- Automatización de comandos (install, lint, format, run, test).
├── pyproject.toml          <- Configuración del formateador (Black) y herramientas de test.
└── setup.cfg               <- Configuración del linter (Flake8) a un máximo de 100 caracteres.
```