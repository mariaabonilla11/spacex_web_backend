"""
Routers de FastAPI para la API de lanzamientos SpaceX

Este módulo contiene todos los endpoints REST de la aplicación,
organizados por funcionalidad.

Routers disponibles:
- launches: Endpoints para operaciones con lanzamientos
  - GET /launches - Obtener todos los lanzamientos
  - GET /launches/date-range - Filtrar por fechas
  - POST /launches/filter - Filtros avanzados
  - GET /launches/{id} - Obtener por ID
  - GET /launches/stats/summary - Estadísticas
  - GET /health - Health check

Todos los endpoints están bajo el prefijo /api/v1
"""

from .launches import router as launches_router

__all__ = [
    "launches_router"
]