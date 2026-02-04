import json
from unittest.mock import patch, MagicMock

# Ahora el import no fallará porque conftest.py ya configuró os.environ
from infrastructure.handlers.async_processor import handler

def test_handler_processes_sqs_record(lambda_context):
    # Simulamos el evento de SQS
    event = {
        "Records": [
            {
                "messageId": "12345",
                "body": json.dumps({
                    "idempotency_key": "tx_test_1",
                    "amount": 1500.50,
                    "currency": "COP"
                })
            }
        ]
    }

    # Mockeamos el caso de uso para que no ejecute lógica real
    with patch('infrastructure.handlers.async_processor.use_case') as mock_use_case:
        handler(event, lambda_context)
        
        # Verificamos que se llamó al caso de uso con los datos validados
        mock_use_case.execute.assert_called_once()
        args = mock_use_case.execute.call_args[0][0]
        assert args["idempotency_key"] == "tx_test_1"
        assert args["amount"] == 1500.50