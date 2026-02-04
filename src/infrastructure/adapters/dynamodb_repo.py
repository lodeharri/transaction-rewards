import boto3
from decimal import Decimal
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger

logger = Logger(service="IngestionService")

class DynamoDBRepository:
    def __init__(self, table_name):
        self.table = boto3.resource('dynamodb').Table(table_name)

    def save_new(self, transaction):
        item = transaction.to_dict()
        if 'amount' in item:
            item['amount'] = Decimal(str(item['amount']))

        try:
            self.table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(idempotency_key)"
            )

            logger.info("Info guarada en dynamodb")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            raise e