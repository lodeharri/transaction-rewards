from unittest.mock import MagicMock
from core.application.use_cases import ProcessIngestionUseCase

def test_process_ingestion_success():
    # Arrange (Preparar)
    mock_repo = MagicMock()
    mock_repo.save_new.return_value = True # Simulamos que se guardó bien
    
    mock_bus = MagicMock()
    
    use_case = ProcessIngestionUseCase(repository=mock_repo, messenger=mock_bus)
    data = {"idempotency_key": "unique_key", "amount": 1000.0, "currency": "COP"}

    # Act (Actuar)
    result = use_case.execute(data)

    # Assert (Afirmar)
    assert result is True
    mock_repo.save_new.assert_called_once() # Verificamos que se llamó a la DB
    mock_bus.publish.assert_called_once()    # Verificamos que se emitió el evento

def test_process_ingestion_duplicate_ignored():
    # Arrange
    mock_repo = MagicMock()
    mock_repo.save_new.return_value = False # Simulamos que ya existe (duplicado)
    mock_bus = MagicMock()
    
    use_case = ProcessIngestionUseCase(mock_repo, mock_bus)
    data = {"idempotency_key": "duplicate_key", "amount": 1000.0, "currency": "COP"}

    # Act
    result = use_case.execute(data)

    # Assert
    assert result is False
    mock_bus.publish.assert_not_called() # Si es duplicado, NO debe publicar evento