from dataclasses import dataclass
from decimal import Decimal

@dataclass
class UserPoints:
    user_id: str
    points: int
    last_tx_id: str

    @staticmethod
    def calculate(amount: Decimal) -> int:
        # Lógica de negocio pura: 1 punto por cada 1000 COP
        return int(amount // 1000)