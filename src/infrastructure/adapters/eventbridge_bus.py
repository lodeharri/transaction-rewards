import boto3
import json
from core.domain.constants import EventNames
from aws_lambda_powertools import Logger

logger = Logger(service="IngestionService")

class EventBridgeMessenger:
    def __init__(self, bus_name: str):
        self.client = boto3.client('events')
        self.bus_name = bus_name

    def publish(self, detail_type: str, payload: dict):
        """
        Publica un evento en el bus personalizado.
        """
        try:
            response = self.client.put_events(
                Entries=[
                    {
                        'Source': EventNames.TRANSACTION_SOURCE,
                        'DetailType': detail_type,
                        'Detail': json.dumps(payload),
                        'EventBusName': self.bus_name
                    }
                ]
            )
            
            # Verificación de fallos parciales de EventBridge
            if response.get('FailedEntryCount', 0) > 0:
                logger.warning(f"Error publicando evento: {response['Entries']}")
                return False
            
            logger.info(f"Evento publicado con exito")
            return True
        except Exception as e:
            print(f"Fallo crítico en EventBridge Adapter: {str(e)}")
            raise e