# SpaceX Web Backend

API REST desarrollada con FastAPI (v0.103.2) que proporciona acceso a datos de lanzamientos de SpaceX almacenados en DynamoDB. Diseñada para servir información de misiones espaciales de forma eficiente y escalable.

## Características

- **API REST completa** con FastAPI
- **Integración con DynamoDB** para almacenamiento de datos
- **Documentación automática** con Swagger/OpenAPI
- **Testing** con pytest
- **Containerización** con Docker
- **Despliegue en AWS ECS** Fargate

## Tecnologías

- **FastAPI 0.103.2** - Framework web moderno
- **Python 3.11** - Lenguaje de programación
- **DynamoDB** - Base de datos NoSQL
- **Boto3** - SDK de AWS para Python
- **Pytest** - Framework de testing
- **Uvicorn** - Servidor ASGI
- **Docker** - Containerización
- **Pydantic** - Validación de datos

## Requisitos Previos

- Python 3.11+
- AWS CLI configurado
- Docker (para containerización)
- Acceso a DynamoDB
- Credenciales AWS válidas

## Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/mariaabonilla11/spacex_web_backend.git
cd spacex_web_backend
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar el archivo de ejemplo y configurar las variables:

```bash
cp .env-example .env
```

Configurar `.env`:

```env
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_DEFAULT_REGION=us-east-1
DYNAMODB_TABLE_NAME=spacex_launches
API_VERSION=v1
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 5. Ejecutar la aplicación

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

La API estará disponible en `http://localhost:8000`

## Docker

### Construcción de la imagen

```bash
docker build -t spacex-backend .
```

### Ejecutar contenedor

```bash
docker run -d -p 8000:8000 --name spacex-backend spacex-backend
```

## Estructura del Proyecto

```
spacex_web_backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── launches.py    # Endpoints de lanzamientos
│   │   │   │   ├── health.py      # Health checks
│   │   │   │   └── stats.py       # Estadísticas
│   │   │   ├── api.py             # Router principal API v1
│   │   │   └── deps.py            # Dependencias
│   │   └── deps.py                # Dependencias globales
│   ├── core/
│   │   ├── config.py              # Configuración
│   │   ├── security.py            # Autenticación
│   │   └── database.py            # Conexión DynamoDB
│   ├── models/
│   │   ├── launch.py              # Modelos de lanzamiento
│   │   └── response.py            # Modelos de respuesta
│   ├── services/
│   │   ├── launch_service.py      # Lógica de negocio
│   │   └── dynamodb_service.py    # Servicio DynamoDB
│   ├── tests/
│   │   ├── test_basic_endpoints.py # Tests de endpoints
│   │   └── conftest.py            # Configuración pytest
│   ├── utils/
│   │   ├── exceptions.py          # Excepciones personalizadas
│   │   └── helpers.py             # Funciones auxiliares
│   └── main.py                    # Punto de entrada
├── requirements.txt               # Dependencias Python
├── Dockerfile                     # Configuración Docker
├── .env-example                   # Variables de entorno ejemplo
└── pytest.ini                    # Configuración pytest
```

## Endpoints Principales

### Lanzamientos

```http
GET /api/v1/launches
```
Obtiene todos los lanzamientos con paginación opcional.

**Parámetros de consulta:**
- `limit` (int): Número máximo de resultados (default: 50)
- `offset` (int): Número de elementos a omitir (default: 0)
- `mission_name` (str): Filtrar por nombre de misión
- `launch_success` (bool): Filtrar por éxito del lanzamiento
- `rocket_name` (str): Filtrar por nombre del cohete

**Respuesta:**
```json
{
  "data": [
    {
      "flight_number": 1,
      "mission_name": "FalconSat",
      "launch_date": "2006-03-24T22:30:00Z",
      "rocket": {
        "rocket_name": "Falcon 1",
        "rocket_type": "falcon1"
      },
      "launch_success": false,
      "details": "Engine failure at 33 seconds..."
    }
  ],
  "total": 109,
  "limit": 50,
  "offset": 0
}
```

```http
GET /api/v1/launches/{flight_number}
```
Obtiene un lanzamiento específico por número de vuelo.

```http
GET /api/v1/launches/stats
```
Obtiene estadísticas generales de lanzamientos.

**Respuesta:**
```json
{
  "total_launches": 109,
  "successful_launches": 103,
  "failed_launches": 5,
  "success_rate": 94.5,
  "most_used_rockets": [
    {"name": "Falcon 9", "count": 95},
    {"name": "Falcon Heavy", "count": 3}
  ]
}
```

### Health Check

```http
GET /api/v1/health
```
Verifica el estado de la API y conexiones.

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "database": "connected"
}
```

## Testing

### Ejecutar pruebas

```bash
pytest app/tests/test_basic_endpoints.py -v -s
```

### Ejecutar pruebas en Docker

```bash
docker exec spacex-backend pytest app/tests/test_basic_endpoints.py -v -s
```

## Documentación API

La documentación interactiva está disponible en:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

En producción:
- **Swagger**: http://spacex-app-alb-1144963660.us-east-1.elb.amazonaws.com/api/v1/docs

## Configuración DynamoDB

### Estructura de la tabla

**Nombre de tabla**: `spacex_launches`

**Esquema de datos:**
```json
{
  "flight_number": 1,
  "mission_name": "FalconSat",
  "launch_date": "2006-03-24T22:30:00.000Z",
  "rocket": {
    "rocket_id": "falcon1",
    "rocket_name": "Falcon 1",
    "rocket_type": "falcon1"
  },
  "launch_success": false,
  "launch_failure_details": {
    "time": 33,
    "altitude": null,
    "reason": "engine failure"
  },
  "details": "Engine failure at 33 seconds and loss of vehicle",
  "links": {
    "mission_patch": "https://images2.imgbox.com/40/e3/GypSkayF_o.png",
    "reddit_campaign": null,
    "reddit_launch": null,
    "reddit_recovery": null,
    "reddit_media": null,
    "presskit": null,
    "article_link": "https://www.space.com/2196-spacex-inaugural-falcon-1-rocket-lost-launch.html",
    "wikipedia": "https://en.wikipedia.org/wiki/DemoSat",
    "video_link": "https://www.youtube.com/watch?v=0a_00nJ_Y88"
  }
}
```

### Configuración de AWS

Asegurar que el usuario/rol tenga los siguientes permisos:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:*:table/spacex_launches"
    }
  ]
}
```

## Despliegue

### Variables de entorno para producción

```env
AWS_ACCESS_KEY_ID=<production_key>
AWS_SECRET_ACCESS_KEY=<production_secret>
AWS_DEFAULT_REGION=us-east-1
DYNAMODB_TABLE_NAME=spacex_launches
API_VERSION=v1
DEBUG=false
CORS_ORIGINS=https://yourdomain.com
```

### Docker para producción

```bash
docker build --platform linux/amd64 -t spacex-backend .
docker tag spacex-backend:latest <ecr-uri>/spacex-app:latest
docker push <ecr-uri>/spacex-app:latest
```

### Health Check en AWS ECS

El servicio incluye un endpoint de health check en `/health` que es utilizado por el Application Load Balancer para verificar el estado de las tareas en ECS.

## Monitoreo y Logging

### Logs estructurados

La aplicación utiliza logging estructurado con los siguientes niveles:

- **ERROR**: Errores de aplicación y excepciones
- **WARNING**: Advertencias y situaciones inusuales
- **INFO**: Información general de operaciones
- **DEBUG**: Información detallada para debugging

## Desarrollo

### Configuración del entorno de desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt
```

### Comandos útiles

```bash
# Ejecutar en modo desarrollo con auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ejecutar tests con coverage
pytest --cov=app tests/

# Generar reporte de coverage
pytest --cov=app --cov-report=html tests/
```

## Troubleshooting

### Problemas comunes

1. **Error de conexión a DynamoDB**
   - Verificar credenciales AWS
   - Confirmar región configurada
   - Validar permisos IAM

2. **Tests fallando**
   - Verificar configuración de test
   - Confirmar mocks de DynamoDB
   - Validar variables de entorno de test

## Licencia

Este proyecto está bajo la Licencia MIT.

## Autor

**Maria del Pilar Bonilla**
- GitHub: [@mariaabonilla11](https://github.com/mariaabonilla11)

## Repositorios Relacionados

- **Frontend**: [spacexweb_frontend](https://github.com/mariaabonilla11/spacexweb_frontend)
- **Infraestructura**: [spacex_web_fullstack](https://github.com/mariaabonilla11/spacex_web_fullstack)
- **Lambda**: [spacex_fullstack](https://github.com/mariaabonilla11/spacex_fullstack)
