from datetime import datetime
import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from main import app
from app.models.launch import LaunchResponse, LaunchStatus

# Cliente de prueba para FastAPI
client = TestClient(app)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_launch():
    """Fixture que provee un lanzamiento de ejemplo"""
    return LaunchResponse(
        id="test-launch-1",
        mission_name="Test Mission",
        rocket_name="Falcon 9",
        launch_date=datetime(2024, 1, 1),
        status=LaunchStatus.SUCCESS,
        details="Test launch details",
        flight_number=100,
        launch_site="Cape Canaveral"
    )

def test_root_endpoint():
    """
    Prueba del endpoint raíz
    Debe retornar un mensaje de bienvenida
    """
    response = client.get("/api")
    assert response.status_code == 200
    assert response.json() == {"message": "SpaceX Launches API - Bienvenido!"}

def test_health_endpoint():
    """
    Prueba del endpoint de health check
    Debe retornar el estado del servicio
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_get_all_launches_success(sample_launch):
    """
    Prueba obtener todos los lanzamientos
    Debe retornar una lista de lanzamientos
    """
    with patch('app.routers.launches.launch_service') as mock_service:
        # Configurar el mock
        mock_service.get_all_launches = AsyncMock(
            return_value=([sample_launch], None, False)
        )
        
        # Hacer la petición
        response = client.get("/api/v1/launches")
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura de la respuesta
        assert "launches" in data
        assert "count" in data
        assert "last_evaluated_key" in data
        assert "has_more" in data
        
        # Verificar contenido
        assert data["count"] == 1
        assert data["has_more"] is False
        assert data["last_evaluated_key"] is None
        
        # Verificar datos del lanzamiento
        launch = data["launches"][0]
        assert launch["id"] == "test-launch-1"
        assert launch["mission_name"] == "Test Mission"
        assert launch["rocket_name"] == "Falcon 9"

@pytest.mark.asyncio
async def test_get_launch_by_id_success(sample_launch):
    """
    Prueba obtener un lanzamiento específico por ID
    Debe retornar los detalles del lanzamiento
    """
    with patch('app.routers.launches.launch_service') as mock_service:
        # Configurar el mock
        mock_service.get_launch_by_id = AsyncMock(return_value=sample_launch)
        
        # Hacer la petición
        response = client.get(f"/api/v1/launches/{sample_launch.id}")
        
        # Verificar respuesta
        assert response.status_code == 200
        launch = response.json()
        
        # Verificar datos del lanzamiento
        assert launch["id"] == sample_launch.id
        assert launch["mission_name"] == sample_launch.mission_name
        assert launch["rocket_name"] == sample_launch.rocket_name
        assert launch["status"] == sample_launch.status.value

@pytest.mark.asyncio
async def test_get_launch_by_id_not_found():
    """
    Prueba obtener un lanzamiento que no existe
    Debe retornar 404 Not Found
    """
    with patch('app.routers.launches.launch_service') as mock_service:
        # Configurar el mock para retornar None (no encontrado)
        mock_service.get_launch_by_id = AsyncMock(return_value=None)
        
        # Hacer la petición
        response = client.get("/api/v1/launches/nonexistent-id")
        
        # Verificar respuesta
        assert response.status_code == 404
        error = response.json()
        assert "detail" in error
        assert "no encontrado" in error["detail"].lower()
