import os
import pytest
from unittest.mock import MagicMock

# Esto se ejecuta INMEDIATAMENTE cuando pytest arranca
os.environ['TABLE_NAME'] = 'TestTable'
os.environ['BUS_NAME'] = 'TestBus'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['POWERTOOLS_SERVICE_NAME'] = 'IngestionService'

# Evita que Powertools intente detectar el entorno de ejecución real de AWS
os.environ['POWERTOOLS_LOGGER_LOG_EVENT'] = 'false'

@pytest.fixture
def lambda_context():
    context = MagicMock()
    context.function_name = "test-function"
    context.aws_request_id = "test-id-123"
    context.invoked_function_arn = "arn:aws:test"
    return context
    