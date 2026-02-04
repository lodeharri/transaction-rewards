import boto3
import os
from aws_lambda_powertools import Logger

logger = Logger(child=True)

class DynamoDBRewardsRepository:
    def __init__(self):
        self.table = boto3.resource('dynamodb').Table(os.environ['REWARDS_TABLE'])

    def update_user_points(self, user_id, points, tx_id):
        try:
            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression="ADD points :p SET last_tx = :tx",
                ConditionExpression="last_tx <> :tx",
                ExpressionAttributeValues={':p': points, ':tx': tx_id}
            )
        except Exception as e:
            logger.warning("Evento ya procesado o fallo en DB", extra={"error": str(e)})