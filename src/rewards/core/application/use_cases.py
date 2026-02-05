from aws_lambda_powertools import Logger
from rewards.core.domain.entities import UserPoints
from shared.observability import get_tracer

tracer = get_tracer("RewardsService")
logger = Logger(service="RewardsService")

class ProcessRewardUseCase:
    def __init__(self, repository):
        self.repository = repository

    @tracer.capture_method
    def execute(self, event_data: dict):
        tx_id = event_data.get("idempotency_key")
        amount = event_data.get("amount", 0)
        user_id = "USER_123" # En producción se extrae del evento

        logger.append_keys(idempotency_key=tx_id)
        
        points_to_add = UserPoints.calculate(amount)
        logger.info(f"Calculando puntos: {points_to_add}")

        self.repository.update_user_points(user_id, points_to_add, tx_id)