# Usar Python 3.11 slim como imagen base
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema si son necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de la aplicación
COPY . .

# Crear usuario no-root para seguridad
RUN adduser --disabled-password --gecos '' --no-create-home appuser && \
    chown -R appuser:appuser /app
USER appuser

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]