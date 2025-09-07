"""
Servicios de lógica de negocio para la API de lanzamientos SpaceX

Este módulo contiene toda la lógica de negocio para operaciones CRUD
y consultas complejas en DynamoDB.

Servicios disponibles:
- LaunchService: Servicio principal para operaciones con lanzamientos
  - Filtros por múltiples criterios  
  - Consultas por rango de fechas
  - Estadísticas y métricas
  - Paginación con DynamoDB
"""

from .launch_service import LaunchService, launch_service

__all__ = [
    "LaunchService",
    "launch_service"
]