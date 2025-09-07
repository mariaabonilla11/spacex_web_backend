import boto3
import aioboto3
from botocore.exceptions import ClientError
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Settings:
    """Configuración simple usando variables de entorno"""
    def __init__(self):
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.dynamodb_table_name = os.getenv('DYNAMODB_TABLE_NAME', 'spacex-launches-dev')
        self.dynamodb_endpoint_url = os.getenv('DYNAMODB_ENDPOINT_URL')
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.debug = os.getenv('DEBUG', 'true').lower() == 'true'

# Instancia global de configuración
settings = Settings()

class DynamoDBClient:
    """Cliente simple para DynamoDB"""
    
    def __init__(self):
        self.table_name = settings.dynamodb_table_name
        self.region = settings.aws_region
        self.endpoint_url = settings.dynamodb_endpoint_url
        
        logger.info(f"DynamoDB client - Tabla: {self.table_name}")
        logger.info(f"Región: {self.region}")
        
    async def get_dynamodb_resource(self):
        """Obtener recurso DynamoDB async"""
        session = aioboto3.Session()
        
        if self.endpoint_url:
            # DynamoDB Local
            return session.resource(
                'dynamodb',
                endpoint_url=self.endpoint_url,
                region_name=self.region,
                aws_access_key_id=settings.aws_access_key_id or 'dummy',
                aws_secret_access_key=settings.aws_secret_access_key or 'dummy'
            )
        else:
            # DynamoDB en AWS
            if settings.aws_access_key_id and settings.aws_secret_access_key:
                return session.resource(
                    'dynamodb',
                    region_name=self.region,
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key
                )
            else:
                return session.resource('dynamodb', region_name=self.region)

# Instancia global del cliente DynamoDB
db_client = DynamoDBClient()