from fastapi import APIRouter, HTTPException, Query, Path, status
from typing import Optional
from datetime import datetime
from app.models.launch import LaunchResponse, LaunchListResponse, LaunchFilter, LaunchStatus, HealthResponse
from app.services.launch_service import launch_service

router = APIRouter()

@router.get(
    "/launches",
    response_model=LaunchListResponse,
    summary="Listar lanzamientos",
    description="Obtiene todos los lanzamientos con soporte de paginación.",
    response_description="Lista paginada de lanzamientos.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "launches": [
                            {
                                "id": "99",
                                "mission_name": "Starlink-9 (v1.0) & BlackSky Global 5-6",
                                "rocket_name": "Falcon 9",
                                "launch_date": "2020-08-07T05:12:00+00:00",
                                "status": "success",
                                "details": "This mission will launch the ninth batch of operational Starlink satellites...",
                                "flight_number": 99,
                                "launch_site": None,
                                "created_at": None,
                                "updated_at": "2025-09-07T12:49:48.951031+00:00"
                            }
                        ],
                        "count": 1,
                        "last_evaluated_key": None,
                        "has_more": False
                    }
                }
            }
        }
    }
)
async def get_all_launches(
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de resultados"),
    last_evaluated_key: Optional[str] = Query(None, description="Clave para paginación")
):
    """
    Retorna una lista paginada de lanzamientos de SpaceX. Permite controlar el número de resultados y la paginación mediante parámetros opcionales.
    """
    try:
        launches, last_key, has_more = await launch_service.get_all_launches(
            limit=limit,
            last_evaluated_key=last_evaluated_key
        )
        
        return LaunchListResponse(
            launches=launches,
            count=len(launches),
            last_evaluated_key=last_key,
            has_more=has_more
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/launches/date-range",
    response_model=LaunchListResponse,
    summary="Listar lanzamientos por rango de fechas",
    description="Obtiene lanzamientos filtrados por un rango de fechas de lanzamiento.",
    response_description="Lista de lanzamientos dentro del rango de fechas.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "launches": [
                            {
                                "id": "25",
                                "mission_name": "OG-2 Mission 2",
                                "rocket_name": "Falcon 9",
                                "launch_date": "2015-12-22T01:29:00+00:00",
                                "status": "success",
                                "details": "Total payload mass was 2,034 kg (4,484 lb)...",
                                "flight_number": 25,
                                "launch_site": None,
                                "created_at": None,
                                "updated_at": "2025-09-07T12:49:47.451030+00:00"
                            }
                        ],
                        "count": 1,
                        "last_evaluated_key": None,
                        "has_more": False
                    }
                }
            }
        }
    }
)
async def get_launches_by_date_range(
    start_date: datetime = Query(..., description="Fecha de inicio (ISO format: YYYY-MM-DDTHH:MM:SS)"),
    end_date: datetime = Query(..., description="Fecha de fin (ISO format: YYYY-MM-DDTHH:MM:SS)"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de resultados"),
    last_evaluated_key: Optional[str] = Query(None, description="Clave para paginación")
):
    """
    Retorna lanzamientos cuyo launch_date esté entre start_date y end_date (inclusive). Permite paginación.
    """
    try:
        if start_date >= end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de inicio debe ser anterior a la fecha de fin"
            )
        
        launches, last_key, has_more = await launch_service.get_launches_by_date_range(
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            last_evaluated_key=last_evaluated_key
        )
        
        return LaunchListResponse(
            launches=launches,
            count=len(launches),
            last_evaluated_key=last_key,
            has_more=has_more
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "/launches/filter",
    response_model=LaunchListResponse,
    summary="Filtrar lanzamientos",
    description="Filtra lanzamientos por misión, cohete, estado, fechas, número de vuelo y sitio de lanzamiento. Permite paginación.",
    response_description="Lista de lanzamientos filtrados.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "launches": [
                            {
                                "id": "99",
                                "mission_name": "Starlink-9 (v1.0) & BlackSky Global 5-6",
                                "rocket_name": "Falcon 9",
                                "launch_date": "2020-08-07T05:12:00+00:00",
                                "status": "success",
                                "details": "This mission will launch the ninth batch of operational Starlink satellites...",
                                "flight_number": 99,
                                "launch_site": None,
                                "created_at": None,
                                "updated_at": "2025-09-07T12:49:48.951031+00:00"
                            }
                        ],
                        "count": 1,
                        "last_evaluated_key": None,
                        "has_more": False
                    }
                }
            }
        },
        422: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "filters", "mission_name"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def filter_launches(filters: LaunchFilter):
    """
    Permite filtrar lanzamientos por múltiples criterios: nombre de misión, cohete, estado, rango de fechas, número de vuelo y sitio de lanzamiento. Los filtros se envían en el body como JSON.
    """
    try:
        if filters.start_date and filters.end_date and filters.start_date >= filters.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de inicio debe ser anterior a la fecha de fin"
            )
        
        launches, last_key, has_more = await launch_service.filter_launches(filters)
        
        return LaunchListResponse(
            launches=launches,
            count=len(launches),
            last_evaluated_key=last_key,
            has_more=has_more
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/launches/{launch_id}", response_model=LaunchResponse)
async def get_launch_by_id(
    launch_id: str = Path(..., description="ID único del lanzamiento")
):
    """
    Obtener un lanzamiento específico por su ID
    """
    try:
        launch = await launch_service.get_launch_by_id(launch_id)
        if not launch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lanzamiento no encontrado"
            )
        return launch
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/launches/stats/summary")
async def get_launches_summary():
    """
    Obtener estadísticas resumidas de los lanzamientos
    
    Retorna:
    - Total de lanzamientos
    - Lanzamientos exitosos, fallidos y próximos
    - Tasa de éxito
    - Cohetes más utilizados
    """
    try:
        # Obtener todos los lanzamientos para calcular estadísticas
        all_launches, _, _ = await launch_service.get_all_launches(limit=1000)
        
        total_launches = len(all_launches)
        successful_launches = sum(1 for launch in all_launches if launch.status == LaunchStatus.SUCCESS)
        failed_launches = sum(1 for launch in all_launches if launch.status == LaunchStatus.FAILED)
        upcoming_launches = sum(1 for launch in all_launches if launch.status == LaunchStatus.UPCOMING)
        
        # Cohetes más utilizados
        rocket_counts = {}
        for launch in all_launches:
            rocket_counts[launch.rocket_name] = rocket_counts.get(launch.rocket_name, 0) + 1
        
        most_used_rockets = sorted(rocket_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_launches": total_launches,
            "successful_launches": successful_launches,
            "failed_launches": failed_launches,
            "upcoming_launches": upcoming_launches,
            "success_rate": round((successful_launches / total_launches * 100), 2) if total_launches > 0 else 0,
            "most_used_rockets": [{"rocket_name": name, "count": count} for name, count in most_used_rockets]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Endpoint de health check para verificar que la API está funcionando
    """
    return HealthResponse(
        status="healthy",
        service="spacex-launches-api",
        timestamp=datetime.utcnow().isoformat()
    )