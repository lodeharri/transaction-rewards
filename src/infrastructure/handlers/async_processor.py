import os
import json
from pydantic import BaseModel, ValidationError
from core.application.use_cases import ProcessIngestionUseCase
from infrastructure.adapters.dynamodb_repo import DynamoDBRepository
from infrastructure.adapters.eventbridge_bus import EventBridgeMessenger
from aws_lambda_powertools import Logger

# Esquema de validación Pydantic
class PaymentInput(BaseModel):
    idempotency_key: str
    amount: float
    currency: str

# Inyección de dependencias (Singleton)
repo = DynamoDBRepository(os.environ['TABLE_NAME'])
bus = EventBridgeMessenger(os.environ['BUS_NAME'])
use_case = ProcessIngestionUseCase(repo, bus)
logger = Logger(service="IngestionService")

@logger.inject_lambda_context
def handler(event, context):
    batch_item_failures = []
    for record in event['Records']:
        message_id = record['messageId']
        body = json.loads(record['body'])
        id_key = body.get('idempotency_key', 'unknown')

        logger.append_keys(idempotency_key=id_key)
        try:
            # body = json.loads(record['body'])
            # Validación de contrato
            validated_data = PaymentInput(**body)

            # Ejecución del negocio
            use_case.execute(validated_data.model_dump())

            logger.info("Ingesta flow completed")
            
        except (ValidationError, Exception) as e:
            logger.error(
                "Error procesando mensaje SQS", 
                exc_info=True, 
                extra={"record_id": record.get('messageId')}
            )
            batch_item_failures.append({"itemIdentifier": message_id})

    return {"batchItemFailures": batch_item_failures}