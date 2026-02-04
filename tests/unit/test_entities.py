import pytest
from core.domain.entities import Transaction
from core.domain.exceptions import BusinessRuleException

def test_transaction_creation_success():
    """Verifica que una transacción válida se cree correctamente."""
    tx = Transaction(idempotency_key="tx_1", amount=100.5, currency="COP")
    assert tx.amount == 100.5
    assert tx.status == "PENDING"

def test_transaction_negative_amount_raises_error():
    """Regla de Negocio: No se permiten montos negativos."""
    with pytest.raises(BusinessRuleException) as exc:
        Transaction(idempotency_key="tx_2", amount=-1, currency="COP")
    assert "monto debe ser positivo" in str(exc.value).lower()

def test_transaction_invalid_currency_raises_error():
    """Regla de Negocio: Solo aceptamos COP por ahora."""
    with pytest.raises(BusinessRuleException):
        Transaction(idempotency_key="tx_3", amount=100, currency="USD")

def test_transaction_to_dict():
    """Verifica que la conversión a diccionario sea correcta para la DB."""
    tx = Transaction(idempotency_key="id_123", amount=50.0, currency="COP")
    d = tx.to_dict()
    assert d["idempotency_key"] == "id_123"
    assert isinstance(d["created_at"], str)