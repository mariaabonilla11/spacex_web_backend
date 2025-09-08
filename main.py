from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import launches
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SpaceX Launches API",
    description="API para consultar lanzamientos espaciales de SpaceX desde DynamoDB",
    version="1.0.0",
    docs_url="/api/v1/docs",  # Cambia la ruta de Swagger UI
    redoc_url="/api/v1/redoc",  # Cambia la ruta de ReDoc
    openapi_url="/api/v1/openapi.json"  # Cambia la ruta del esquema OpenAPI
)

# Configurar CORS para permitir conexiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas
app.include_router(launches.router, prefix="/api/v1", tags=["launches"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api")
async def root():
    return {"message": "SpaceX Launches API - Bienvenido!"}