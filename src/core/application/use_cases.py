from core.domain.entities import Transaction
from core.domain.constants import EventNames
from aws_lambda_powertools import Logger

logger = Logger(service="IngestionService")

class ProcessIngestionUseCase:
    def __init__(self, repository, messenger):
        self.repository = repository
        self.messenger = messenger

    def execute(self, data: dict):
        # 1. Crear Entidad y validar reglas de negocio
        transaction = Transaction(
            idempotency_key=data['idempotency_key'],
            amount=data['amount'],
            currency=data['currency']
        )
        logger.info(f"Procesando transacción:", extra={"amount": transaction.amount, "currency": transaction.currency})

        # 2. Guardar en DB con Idempotencia
        if not self.repository.save_new(transaction):
            logger.warning(f"Transacción duplicada detectada: {transaction.idempotency_key}")
            print(f"Transacción duplicada detectada: {transaction.idempotency_key}")
            return False

        # 3. Publicar evento para otros microservicios
        self.messenger.publish(
            detail_type=EventNames.TRANSACTION_RECEIVED,
            payload=transaction.to_dict()
        )
        return True