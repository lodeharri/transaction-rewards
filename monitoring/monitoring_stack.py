from aws_cdk import (
    Stack,
    aws_cloudwatch as cw
)
from constructs import Construct

class MonitoringStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # DASHBOARD ÚNICO
        dashboard = cw.Dashboard(self, "BoldMainDashboard",
            dashboard_name="Salud-Sistema-Pagos"
        )

        # WIDGET 1: Mensajes en la DLQ (Si es > 0, algo anda muy mal)
        dashboard.add_widgets(cw.GraphWidget(
            title="Mensajes Fallidos (DLQ)",
            left=[cw.Metric(
                namespace="AWS/SQS",
                metric_name="ApproximateNumberOfMessagesVisible",
                dimensions_map={"QueueName": "IngestionDLQ"}
            )]
        ))
