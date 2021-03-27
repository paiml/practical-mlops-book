from azureml.core.webservice import AciWebservice

aciconfig = AciWebservice.deploy_configuration(
    cpu_cores=1,
    memory_gb=1,
    tags={"demo": "onnx"},
    description="web service for MNIST ONNX model",
)

from azureml.core.model import Model

aci_service_name = "onnx-roberta-demo"
aci_service = Model.deploy(ws, aci_service_name, [model], inference_config, aci_config)
aci_service.wait_for_deployment(True)
