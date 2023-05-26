
# Dto for ProvisionRequests does not exist as openapi model.
# These models are the counterparts to the PojoObjects


from typing import Any, Dict

# pylint: disable=no-name-in-module
from pydantic import BaseModel


# extensions/control-plane/provision/provision-http/src/main/java/org/eclipse/edc/connector/provision/http/impl/HttpProvisionerRequest.java
class HttpProvisionerRequest(BaseModel):
    assetId: str
    transferProcessId: str
    callbackAddress: str
    resourceDefinitionId: str
    policy: Any


# extensions/control-plane/provision/provision-http/src/main/java/org/eclipse/edc/connector/provision/http/webhook/ProvisionerWebhookRequest.java
class ProvisionerWebhookRequest(BaseModel):
    edctype: str = "dataspaceconnector:provisioner-callback-request"
    resourceDefinitionId: str
    assetId: str
    resourceName: str
    contentDataAddress: Dict[str, Dict[str, str]]
    apiKeyJwt: str = "unused"
    hasToken: bool = False
