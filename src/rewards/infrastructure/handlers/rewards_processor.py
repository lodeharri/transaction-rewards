import json
from aws_lambda_powertools import Logger
from rewards.infrastructure.adapters.dynamodb_rewards_repo import DynamoDBRewardsRepository
from rewards.core.application.use_cases import ProcessRewardUseCase
from ..schemas.payment_event import PaymentEventDTO
from pydantic import ValidationError

logger = Logger(service="RewardsService")
repo = DynamoDBRewardsRepository()
use_case = ProcessRewardUseCase(repo)

@logger.inject_lambda_context
def handler(event, context):
    # En EventBridge, el dato útil viene en la llave 'detail'
    detail = event.get('detail', {})
    
    try:
        validated_data = PaymentEventDTO(**detail)
        use_case.execute(validated_data.model_dump())
    except (ValidationError, Exception) as e:
        logger.error("Error procesando puntos", exc_info=True)
        raise e