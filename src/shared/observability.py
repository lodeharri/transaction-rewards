from aws_lambda_powertools import Tracer

# El tracer detecta automáticamente si está en AWS y habilita el envío de segmentos
def get_tracer(service_name: str):
    return Tracer(service=service_name)