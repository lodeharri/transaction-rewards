from dataclasses import dataclass, field
from datetime import datetime
from .exceptions import BusinessRuleException

@dataclass
class Transaction:
    idempotency_key: str
    amount: float
    currency: str
    status: str = "PENDING"
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.amount <= 0:
            raise BusinessRuleException("El monto debe ser positivo.")
        if self.currency != "COP": # Bold opera principalmente en Colombia
            raise BusinessRuleException("Solo se aceptan transacciones en COP.")

    def to_dict(self):
        return {
            "idempotency_key": self.idempotency_key,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }