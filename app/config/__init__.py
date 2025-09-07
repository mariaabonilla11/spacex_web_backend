"""
Configuración de la aplicación SpaceX Launches API

Este módulo contiene la configuración necesaria para la aplicación:
- Configuración de base de datos DynamoDB
- Variables de entorno
- Cliente de conexión a DynamoDB

Componentes principales:
- Settings: Configuración usando variables de entorno
- DynamoDBClient: Cliente para operaciones con DynamoDB
- db_client: Instancia global del cliente
"""

from .database import (
    Settings,
    DynamoDBClient,
    db_client,
    settings
)

__all__ = [
    "Settings",
    "DynamoDBClient", 
    "db_client",
    "settings"
]