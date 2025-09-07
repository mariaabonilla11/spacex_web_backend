from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum
from decimal import Decimal

class LaunchStatus(str, Enum):
    """Estados posibles de un lanzamiento"""
    SUCCESS = "success"
    FAILED = "failed"
    UPCOMING = "upcoming"

class LaunchResponse(BaseModel):
    """Modelo de respuesta para lanzamientos"""
    id: str = Field(..., description="ID único del lanzamiento")
    mission_name: str = Field(..., description="Nombre de la misión")
    rocket_name: str = Field(..., description="Nombre del cohete")
    launch_date: datetime = Field(..., description="Fecha y hora del lanzamiento")
    status: LaunchStatus = Field(..., description="Estado del lanzamiento")
    details: Optional[str] = Field(None, description="Detalles adicionales")
    flight_number: Optional[int] = Field(None, description="Número de vuelo")
    launch_site: Optional[str] = Field(None, description="Sitio de lanzamiento")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }

class LaunchFilter(BaseModel):
    """Modelo para filtrar lanzamientos"""
    mission_name: Optional[str] = Field(None, description="Filtro por nombre de misión")
    rocket_name: Optional[str] = Field(None, description="Filtro por nombre del cohete")
    status: Optional[LaunchStatus] = Field(None, description="Filtro por estado")
    start_date: Optional[datetime] = Field(None, description="Fecha de inicio del rango")
    end_date: Optional[datetime] = Field(None, description="Fecha final del rango")
    launch_site: Optional[str] = Field(None, description="Filtro por sitio de lanzamiento")
    flight_number_min: Optional[int] = Field(None, ge=1, description="Número de vuelo mínimo")
    flight_number_max: Optional[int] = Field(None, ge=1, description="Número de vuelo máximo")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Límite de resultados")
    last_evaluated_key: Optional[str] = Field(None, description="Clave para paginación")

class LaunchListResponse(BaseModel):
    """Respuesta para listas de lanzamientos con paginación"""
    launches: List[LaunchResponse] = Field(..., description="Lista de lanzamientos")
    count: int = Field(..., ge=0, description="Número de resultados")
    last_evaluated_key: Optional[str] = Field(None, description="Clave para siguiente página")
    has_more: bool = Field(False, description="Hay más resultados disponibles")

class HealthResponse(BaseModel):
    """Respuesta para health check"""
    status: str = Field(...)
    service: str = Field(...)
    timestamp: str = Field(...)