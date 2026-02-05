from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as targets,
    aws_ssm as ssm,
    RemovalPolicy,
    aws_cloudwatch as cw,
    aws_cloudwatch_actions as cw_actions,
)
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from constructs import Construct

class RewardsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Tabla de puntos
        table = dynamodb.Table(
            self, "RewardsTable",
            partition_key=dynamodb.Attribute(name="user_id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        # 2. Leer nombre del Bus desde SSM (Desacoplamiento total)
        bus_name = ssm.StringParameter.value_for_string_parameter(self, "/bold/infra/payment-bus-name")
        bus = events.EventBus.from_event_bus_name(self, "ImportedBus", bus_name)

        powertools_layer = _lambda.LayerVersion.from_layer_version_arn(
            self, "PowertoolsLayer",
            layer_version_arn="arn:aws:lambda:us-east-2:017000801446:layer:AWSLambdaPowertoolsPythonV2:60"
        )
        
        layer = PythonLayerVersion(self, "LibLayer", entry="layers/pydantic_layer", compatible_runtimes=[_lambda.Runtime.PYTHON_3_11])
        
        # 3. Función Procesadora
        rewards_fn = _lambda.Function(
            self, "RewardsFn",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="rewards.infrastructure.handlers.rewards_processor.handler",
            code=_lambda.Code.from_asset("src"),
            layers=[powertools_layer, layer],
            environment={"REWARDS_TABLE": table.table_name},
        )
        table.grant_read_write_data(rewards_fn)

        # 4. Regla: Solo procesar transacciones recibidas
        rule = events.Rule(
            self, "OnTransactionReceived",
            event_bus=bus,
            event_pattern=events.EventPattern(
                source=["bold.payments.ingestion"],
                detail_type=["TransactionReceived"]
            )
        )
        rule.add_target(targets.LambdaFunction(rewards_fn))

        # 5. Alarmas
        error_alarm = cw.Alarm(self, "RewardsErrorAlarm",
            metric=rewards_fn.metric_errors(),
            threshold=1, # Con 1 solo error ya nos interesa saber
            evaluation_periods=1,
            datapoints_to_alarm=1,
            alarm_description="Alarma si falla el procesamiento de puntos"
        )
