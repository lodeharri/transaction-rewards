class BusinessRuleException(Exception):
    """Excepción base para reglas de negocio de Bold."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)