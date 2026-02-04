class EventNames:
    TRANSACTION_SOURCE = "bold.payments.ingestion"
    TRANSACTION_RECEIVED = "TransactionReceived"

class InfrastructureNames:
    PAYMENT_BUS = "BoldPaymentBus"
    INGESTION_QUEUE = "TransactionIngestionQueue"
    TRANSACTIONS_TABLE = "BoldTransactions"