from aws_cdk import (
    Stack, 
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_sqs as sqs,
    aws_apigateway as apigw,
    aws_iam as iam,
    aws_lambda_event_sources as sources,
    Duration,
    RemovalPolicy,
    aws_ssm as ssm
)
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from constructs import Construct
from src.core.domain.constants import InfrastructureNames

class TransactionsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Capa de Datos (DynamoDB)
        table = dynamodb.Table(
            self, "TransactionsTable",
            partition_key=dynamodb.Attribute(name="idempotency_key", type=dynamodb.AttributeType.STRING),
            table_name=InfrastructureNames.TRANSACTIONS_TABLE,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # 2. Comunicación (EventBridge Bus)
        bus = events.EventBus(self, "PaymentBus", event_bus_name=InfrastructureNames.PAYMENT_BUS)

        ssm.StringParameter(self, "BusNameParameter",
            parameter_name="/bold/infra/payment-bus-name",
            string_value=bus.event_bus_name,
            description="Nombre del Bus de pagos para otros microservicios"
        )

        dlq = sqs.Queue(self, "IngestionDLQ",
            retention_period=Duration.days(14) # Guardamos 14 días para investigar
        )

        # 3. Buffer de Alta Concurrencia (SQS)
        queue = sqs.Queue(
            self, "IngestionQueue",
            queue_name=InfrastructureNames.INGESTION_QUEUE,
            visibility_timeout=Duration.seconds(30),
            dead_letter_queue=sqs.DeadLetterQueue(
                queue=dlq,
                max_receive_count=3
            )
        )

        # 4. API Gateway con Integración Directa a SQS (Sin Lambda de entrada)
        api_role = iam.Role(self, "ApiRole", assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"))
        queue.grant_send_messages(api_role)

        api = apigw.RestApi(self, "TransactionApi")
        
        sqs_integration = apigw.AwsIntegration(
            service="sqs",
            path=f"{self.account}/{queue.queue_name}",
            integration_http_method="POST",
            options=apigw.IntegrationOptions(
                credentials_role=api_role,
                request_parameters={'integration.request.header.Content-Type': "'application/x-www-form-urlencoded'"},
                request_templates={"application/json": "Action=SendMessage&MessageBody=$util.urlEncode($input.body)"},
                integration_responses=[{"statusCode": "200", "responseTemplates": {"application/json": '{"status": "accepted"}'}}]
            )
        )
        api.root.add_resource("ingest").add_method("POST", sqs_integration, method_responses=[{"statusCode": "200"}])

        powertools_layer = _lambda.LayerVersion.from_layer_version_arn(
            self, "PowertoolsLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:017000801446:layer:AWSLambdaPowertoolsPythonV2:60"
        )

        # 5. Lambda Processor con Permisos (El "Trabajador")
        layer = PythonLayerVersion(self, "LibLayer", entry="layers/pydantic_layer", compatible_runtimes=[_lambda.Runtime.PYTHON_3_11])

        # 5. Función Procesadora con tracing
        processor_fn = _lambda.Function(
            self, "ProcessorFn",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="infrastructure.handlers.async_processor.handler",
            code=_lambda.Code.from_asset("src"), # SOLO apuntamos a 'src'
            layers=[powertools_layer, layer],
            tracing=_lambda.Tracing.ACTIVE,
            environment={
                "TABLE_NAME": table.table_name,
                "BUS_NAME": bus.event_bus_name
            },
            #log_retention=logs.RetentionDays.ONE_WEEK # Borra automáticamente logs de más de 7 días
            #reserved_concurrent_executions=5 # Freno de seguridad para proteger la DB
        )

        # 6. PERMISOS Y CONECTIVIDAD
        table.grant_read_write_data(processor_fn)
        bus.grant_put_events_to(processor_fn)
        queue.grant_consume_messages(processor_fn)
        
        # Cableado SQS -> Lambda
        processor_fn.add_event_source(sources.SqsEventSource(
            queue,
            batch_size=10,
            max_batching_window=Duration.seconds(5),
            # ACTIVAR reporte de fallos parciales
            report_batch_item_failures=True
        ))