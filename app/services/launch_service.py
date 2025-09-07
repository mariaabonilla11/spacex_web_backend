import uuid
import json
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from app.models.launch import LaunchResponse, LaunchStatus, LaunchFilter
from app.config.database import db_client
import logging

logger = logging.getLogger(__name__)

class LaunchService:
    """Servicio para manejar consultas de lanzamientos en DynamoDB"""
    
    def __init__(self):
        self.table_name = db_client.table_name
    
    def _convert_decimals(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convertir valores Decimal de DynamoDB a float para compatibilidad con Pydantic"""
        if isinstance(item, dict):
            return {key: self._convert_decimals(value) for key, value in item.items()}
        elif isinstance(item, list):
            return [self._convert_decimals(element) for element in item]
        elif isinstance(item, Decimal):
            return float(item)
        else:
            return item
    
    def _item_to_launch_response(self, item: Dict[str, Any]) -> LaunchResponse:
        """Convertir item de DynamoDB a modelo LaunchResponse"""
        try:
            # Convertir Decimals a floats
            item = self._convert_decimals(item)
            
            return LaunchResponse(
                id=item['launch_id'],
                mission_name=item['mission_name'],
                rocket_name=item['rocket_name'],
                launch_date=datetime.fromisoformat(item['launch_date']),
                status=LaunchStatus(item['status']),
                details=item.get('details'),
                flight_number=item.get('flight_number'),
                launch_site=item.get('launch_site')
            )
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing launch data: {e}, item: {item}")
            raise ValueError(f"Formato de datos inválido: {e}")
    
    async def get_all_launches(
        self,
        limit: int = 100,
        last_evaluated_key: Optional[str] = None
    ) -> Tuple[List[LaunchResponse], Optional[str], bool]:
        """Obtener todos los lanzamientos con paginación"""
        try:
            dynamodb_resource = await db_client.get_dynamodb_resource()

            async with dynamodb_resource as dynamodb:
                table = await dynamodb.Table(self.table_name)

                scan_kwargs = {
                    'Limit': limit
                }

                if last_evaluated_key:
                    scan_kwargs['ExclusiveStartKey'] = {'launch_id': last_evaluated_key}

                response = await table.scan(**scan_kwargs)

                launches = []
                for item in response.get('Items', []):
                    try:
                        launch = self._item_to_launch_response(item)
                        launches.append(launch)
                    except ValueError as e:
                        logger.warning(f"Skipping invalid launch item: {e}")
                        continue

                # Ordenar por fecha de lanzamiento (más reciente primero)
                launches.sort(key=lambda x: x.launch_date, reverse=True)

                last_key = None
                has_more = False
                if 'LastEvaluatedKey' in response and 'launch_id' in response['LastEvaluatedKey']:
                    last_key = response['LastEvaluatedKey']['launch_id']
                    has_more = True

                logger.info(f"Retrieved {len(launches)} launches")
                return launches, last_key, has_more

        except Exception as e:
            logger.error(f"Error fetching all launches: {e}")
            raise Exception(f"Error obteniendo lanzamientos: {str(e)}")
    
    async def get_launches_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
        last_evaluated_key: Optional[str] = None
    ) -> Tuple[List[LaunchResponse], Optional[str], bool]:
        """Obtener lanzamientos por rango de fechas"""
        try:
            dynamodb_resource = await db_client.get_dynamodb_resource()

            async with dynamodb_resource as dynamodb:
                table = await dynamodb.Table(self.table_name)

                # Usar scan con filtro de fecha
                filter_expression = Attr('launch_date').between(
                    start_date.isoformat(),
                    end_date.isoformat()
                )

                scan_kwargs = {
                    'FilterExpression': filter_expression,
                    'Limit': limit
                }

                if last_evaluated_key:
                    scan_kwargs['ExclusiveStartKey'] = {'launch_id': last_evaluated_key}

                response = await table.scan(**scan_kwargs)

                launches = []
                for item in response.get('Items', []):
                    try:
                        launch = self._item_to_launch_response(item)
                        launches.append(launch)
                    except ValueError as e:
                        logger.warning(f"Skipping invalid launch item: {e}")
                        continue

                # Ordenar por fecha de lanzamiento
                launches.sort(key=lambda x: x.launch_date)

                last_key = None
                has_more = False
                if 'LastEvaluatedKey' in response and 'launch_id' in response['LastEvaluatedKey']:
                    last_key = response['LastEvaluatedKey']['launch_id']
                    has_more = True

                logger.info(f"Retrieved {len(launches)} launches for date range {start_date} to {end_date}")
                return launches, last_key, has_more

        except Exception as e:
            logger.error(f"Error fetching launches by date range: {e}")
            raise Exception(f"Error obteniendo lanzamientos por fecha: {str(e)}")
    
    async def filter_launches(self, filters: LaunchFilter) -> Tuple[List[LaunchResponse], Optional[str], bool]:
        """Filtrar lanzamientos por múltiples criterios"""
        try:
            dynamodb_resource = await db_client.get_dynamodb_resource()

            async with dynamodb_resource as dynamodb:
                table = await dynamodb.Table(self.table_name)

                # Construir expresión de filtro dinámicamente
                filter_expressions = []

                if filters.mission_name:
                    filter_expressions.append(
                        Attr('mission_name').contains(filters.mission_name)
                    )

                if filters.rocket_name:
                    filter_expressions.append(
                        Attr('rocket_name').contains(filters.rocket_name)
                    )

                if filters.status:
                    filter_expressions.append(
                        Attr('status').eq(filters.status.value)
                    )

                if filters.launch_site:
                    filter_expressions.append(
                        Attr('launch_site').contains(filters.launch_site)
                    )

                # Filtros de fecha
                if filters.start_date and filters.end_date:
                    filter_expressions.append(
                        Attr('launch_date').between(
                            filters.start_date.isoformat(),
                            filters.end_date.isoformat()
                        )
                    )
                elif filters.start_date:
                    filter_expressions.append(
                        Attr('launch_date').gte(filters.start_date.isoformat())
                    )
                elif filters.end_date:
                    filter_expressions.append(
                        Attr('launch_date').lte(filters.end_date.isoformat())
                    )

                # Filtros de número de vuelo
                if filters.flight_number_min and filters.flight_number_max:
                    filter_expressions.append(
                        Attr('flight_number').between(filters.flight_number_min, filters.flight_number_max)
                    )
                elif filters.flight_number_min:
                    filter_expressions.append(
                        Attr('flight_number').gte(filters.flight_number_min)
                    )
                elif filters.flight_number_max:
                    filter_expressions.append(
                        Attr('flight_number').lte(filters.flight_number_max)
                    )

                # Combinar filtros con AND
                filter_expression = None
                if filter_expressions:
                    filter_expression = filter_expressions[0]
                    for expr in filter_expressions[1:]:
                        filter_expression = filter_expression & expr

                scan_kwargs = {
                    'Limit': filters.limit or 100
                }

                if filter_expression:
                    scan_kwargs['FilterExpression'] = filter_expression

                if filters.last_evaluated_key:
                    scan_kwargs['ExclusiveStartKey'] = {'launch_id': filters.last_evaluated_key}

                response = await table.scan(**scan_kwargs)

                launches = []
                for item in response.get('Items', []):
                    try:
                        launch = self._item_to_launch_response(item)
                        launches.append(launch)
                    except ValueError as e:
                        logger.warning(f"Skipping invalid launch item: {e}")
                        continue

                # Ordenar por fecha de lanzamiento (más reciente primero)
                launches.sort(key=lambda x: x.launch_date, reverse=True)

                last_key = None
                has_more = False
                if 'LastEvaluatedKey' in response and 'launch_id' in response['LastEvaluatedKey']:
                    last_key = response['LastEvaluatedKey']['launch_id']
                    has_more = True

                logger.info(f"Filtered {len(launches)} launches")
                return launches, last_key, has_more

        except Exception as e:
            logger.error(f"Error filtering launches: {e}")
            raise Exception(f"Error filtrando lanzamientos: {str(e)}")
    
    async def get_launch_by_id(self, launch_id: str) -> Optional[LaunchResponse]:
        """Obtener un lanzamiento específico por ID"""
        try:
            dynamodb_resource = await db_client.get_dynamodb_resource()

            async with dynamodb_resource as dynamodb:
                table = await dynamodb.Table(self.table_name)

                response = await table.get_item(Key={'launch_id': launch_id})

                if 'Item' in response:
                    logger.info(f"Found launch: {launch_id}")
                    return self._item_to_launch_response(response['Item'])

                logger.info(f"Launch not found: {launch_id}")
                return None

        except Exception as e:
            logger.error(f"Error fetching launch by ID {launch_id}: {e}")
            raise Exception(f"Error obteniendo lanzamiento: {str(e)}")

# Instancia singleton del servicio
launch_service = LaunchService()