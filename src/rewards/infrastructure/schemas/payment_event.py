from pydantic import BaseModel, Field

class PaymentEventDTO(BaseModel):
    idempotency_key: str
    amount: float = Field(gt=0)
    currency: str