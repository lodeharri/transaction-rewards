API Gateway (Decoupling): Se utiliza una integración directa a SQS para evitar latencia de cómputo y Cold Starts en la frontera del sistema.

SQS (Buffer): Actúa como un nivelador de carga (Load Leveling), permitiendo que el sistema reciba miles de transacciones por segundo sin saturar los recursos internos.

Lambda Concurrency Control: Se define un límite de ejecuciones concurrentes (reserved_concurrent_executions) para proteger la integridad de la base de datos y evitar el agotamiento de recursos.

DynamoDB (Idempotencia): La persistencia se realiza con expresiones condicionales para garantizar que cada idempotency_key sea única, permitiendo reintentos seguros desde la cola.

Para revisar los logs por idempotency_key en logs insigths:

fields @timestamp, message, level, service
| filter idempotency_key = "123asd123"
| sort @timestamp asc

graph LR
    subgraph "Nivel de Entrada (Alta Escala)"
    A[Cliente/CURL] -->|HTTP POST| B[API Gateway]
    B -->|Service Integration| C[(Amazon SQS)]
    end

    subgraph "Procesamiento (Backpressure)"
    C -->|Trigger Batch| D[Lambda Processor]
    D -->|Instancias Máximas: 50| E[(DynamoDB)]
    D -->|Evento de Negocio| F[EventBridge Bus]
    end

    style B fill:#f96,stroke:#333,stroke-width:2px
    style C fill:#ff9,stroke:#333,stroke-width:2px
    style D fill:#f66,stroke:#333,stroke-width:2px
    style E fill:#69f,stroke:#333,stroke-width:4px