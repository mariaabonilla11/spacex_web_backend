"""
SpaceX Launches API

API para consultar lanzamientos espaciales desde DynamoDB
Desarrollado con FastAPI y boto3

Módulos principales:
- models: Modelos Pydantic para validación de datos
- services: Lógica de negocio para operaciones CRUD
- routers: Endpoints de la API REST
- config: Configuración de base de datos y aplicación
"""

__version__ = "1.0.0"
__author__ = "SpaceX Launches Team"
__description__ = "API para consultar lanzamientos espaciales de SpaceX"