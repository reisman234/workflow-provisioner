"""
Provisioner module which is used by edc-connector.
Provisions the workflow-api for a requested service
"""
import asyncio
import os
import subprocess
import tempfile
import uuid
from threading import Thread
from typing import List
import time
from fastapi import FastAPI, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND
import requests

from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

from .edc.connector import EdcClient
from .edc.provision_request import HttpProvisionerRequest, ProvisionerWebhookRequest

from .logging import logger

models.Base.metadata.create_all(bind=engine)

provisioner = FastAPI()

# CONFIG

WF_API_ROOT_PATH = os.getenv("WF_API_ROOT_PATH", "workflowapi/api/")
logger.info("WF_API_ROOT_PATH: %s", WF_API_ROOT_PATH)

# set a static access token which is used for a deployed workflow-api
WF_API_STATIC_ACCESS_TOKEN = os.getenv("WF_API_STATIC_ACCESS_TOKEN")

BACKEND_ENTRYPOINT = os.getenv("WF_PROVISIONER_BACKEND_ENTRYPOINT")
if not BACKEND_ENTRYPOINT:
    raise ValueError("unspecified variable: WF_PROVISIONER_BACKEND_ENTRYPOINT")
logger.info("BACKEND_ENTRYPOINT: %s", BACKEND_ENTRYPOINT)

WF_API_WF_BACKEND_DATA_SIDE_CAR = os.getenv("WF_API_WF_BACKEND_DATA_SIDE_CAR")
if not WF_API_WF_BACKEND_DATA_SIDE_CAR:
    raise ValueError("unspecified variable: WF_API_WF_BACKEND_DATA_SIDE_CAR")
logger.info("WF_API_WF_BACKEND_DATA_SIDE_CAR: %s", WF_API_WF_BACKEND_DATA_SIDE_CAR)

WF_API_WF_BACKEND_REGISTRY_SECRET = os.getenv("WF_API_WF_BACKEND_REGISTRY_SECRET")
logger.info("WF_API_WF_BACKEND_REGISTRY_SECRET: %s", WF_API_WF_BACKEND_REGISTRY_SECRET)

# dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_subcommand(cmd: List[str]):

    try:
        output = subprocess.run(
            cmd,
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as err:
        logger.debug("execution of command \"%s\" failed with %s", cmd, err.stderr)
        raise RuntimeError("running subcommand failed") from err

    return output


@provisioner.on_event("startup")
async def startup():

    cmd = "kubectl get --raw /healthz"

    result = run_subcommand(cmd.split())

    logger.info(result.stdout)


def get_consumer_connector_id(transferProcessId: str):

    edc_client = EdcClient()

    contract_id = edc_client.get_transfer_process(transfer_process_id=transferProcessId)
    contract_agreement = edc_client.get_contract_agreement(contract_id=contract_id.dataRequest.contractId)

    return contract_agreement.consumerAgentId


def handle_edc_request(provisioner_request: HttpProvisionerRequest, db: Session):

    # TODO do request to receive consumer_connector_id
    consumer_connector_id = get_consumer_connector_id(provisioner_request.transferProcessId)

    consumer = crud.get_consumer_by_consumer_id(db,
                                                consumer_id=consumer_connector_id)

    if not consumer:

        workflow_backend_id = uuid.uuid4()
        # consumer unknown deploy workflow_api
        logger.debug("consumer unknown with id=%s, deploy workflow_backend with id=%s",
                     consumer_connector_id, workflow_backend_id)

        access_token = str(uuid.uuid4())
        if WF_API_STATIC_ACCESS_TOKEN:
            access_token = WF_API_STATIC_ACCESS_TOKEN

        deploy_workflow_api(workflow_backend_id=workflow_backend_id,
                            workflow_api_access_token=access_token)

        consumer = crud.create_consumer(db=db,
                                        consumer=schemas.ConsumerCreate(
                                            id=consumer_connector_id,
                                            workflow_backend_id=workflow_backend_id,
                                            access_token=access_token)
                                        )

    if not crud.consumer_has_workflow_asset(
            db=db,
            consumer_id=consumer.id,
            workflow_asset_id=provisioner_request.assetId):

        crud.create_workflow_asset(db=db,
                                   asset=schemas.WorkflowAsset(id=provisioner_request.assetId),
                                   consumer_id=consumer_connector_id)

    data = ProvisionerWebhookRequest(
        resourceDefinitionId=provisioner_request.resourceDefinitionId,
        assetId=provisioner_request.assetId,
        resourceName="test",
        contentDataAddress={"properties": {
            "type": "HttpData",
            "baseUrl": f"http://workflow-provisioner:8888/details?consumer_id={consumer.id}"
        }}
    )

    completeUrl = f"{provisioner_request.callbackAddress}/{provisioner_request.transferProcessId}/provision"

    try:
        logger.debug("callback to %s", completeUrl)
        response = requests.post(url=completeUrl,
                                 json=data.dict(),
                                 headers={"x-api-key": "password"})
    except ConnectionError as connection_error:
        print(f"ConnectionError: {connection_error}")

    logger.debug("work finished: callback request status: %s", response.status_code)


def deploy_workflow_api(workflow_backend_id: str,
                        workflow_api_access_token: str):

    logger.debug("do_provision")

    user_name = "dummy-user"
    user_namespace = workflow_backend_id

    cmd_add_repo = [
        "helm", "repo", "add", "minio", "https://charts.min.io/"
    ]

    workflow_api_env = f"""
    FASTAPI_ROOT_PATH=/{WF_API_ROOT_PATH}{workflow_backend_id}/
    """

    workflow_api_config = f"""
    [workflow_api]
    workflow_api_user = dummy-user
    workflow_api_access_token = {workflow_api_access_token}

    workflow_backend = kubernetes
    workflow_backend_namespace = {workflow_backend_id}
    workflow_backend_image_pull_secret = {WF_API_WF_BACKEND_REGISTRY_SECRET}
    workflow_backend_data_side_car_image = {WF_API_WF_BACKEND_DATA_SIDE_CAR}
    workflow_k8s_backend_job_storage_type = PERSISTENT_VOLUME_CLAIM
    # workflow_k8s_backend_job_storage_size = 5Gi

    [minio]
    endpoint = minio:9000
    access_key = rootuser
    secret_key = rootpass123
    secure = false
    """

    k8s_namespace = f"""
    apiVersion: v1
    kind: Namespace
    metadata:
      creationTimestamp: null
      name: {user_namespace}
      labels:
        project: gx4ki
    """

    k8s_ingress_manifest = f"""
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: workflow-api-ingress
      labels:
        name: workflow-api-ingress
      annotations:
        nginx.ingress.kubernetes.io/rewrite-target: /$2
    spec:
      rules:
      - host: {BACKEND_ENTRYPOINT}
        http:
          paths:
          - pathType: Prefix
            path: /{WF_API_ROOT_PATH}{workflow_backend_id}(/|$)(.*)
            backend:
              service:
                name: workflow-api
                port:
                  number: 8080
    """

    with tempfile.NamedTemporaryFile(mode="w", encoding="utf8") as tmp_file, \
            tempfile.NamedTemporaryFile(mode="w", encoding="utf8") as tmp_env_file,\
            tempfile.NamedTemporaryFile(mode="w", encoding="utf8") as tmp_k8s_ingress,\
            tempfile.NamedTemporaryFile(mode="w", encoding="utf8") as tmp_k8s_namespace:

        tmp_k8s_namespace.write(k8s_namespace)
        tmp_k8s_namespace.flush()

        tmp_file.write(workflow_api_config)
        tmp_file.flush()

        tmp_env_file.write(workflow_api_env)
        tmp_env_file.flush()

        tmp_k8s_ingress.write(k8s_ingress_manifest)
        tmp_k8s_ingress.flush()

        cmd_deploy_workflow_api = [
            f"kubectl apply -f {tmp_k8s_namespace.name}",
            f"cat {tmp_file.name}",
            f"kubectl -n {user_namespace} create secret generic workflow-api-config --from-file=workflow-api.cfg={tmp_file.name}",
            f"kubectl -n {user_namespace} create configmap workflow-api-env --from-env-file={tmp_env_file.name}",
            f"kubectl -n {user_namespace} apply -f ./k8s/workflow-api-service-account.yaml",
            f"kubectl -n {user_namespace} apply -f ./k8s/workflow-api-demo-assets.yml",
            f"kubectl -n {user_namespace} apply -f ./k8s/workflow-api.yaml",
            f"kubectl -n {user_namespace} apply -f {tmp_k8s_ingress.name}",
        ]
        if os.path.exists("./k8s/secrets/registry-secret.yaml"):
            cmd_deploy_workflow_api.append(
                f"kubectl -n {user_namespace} apply -f ./k8s/secrets/registry-secret.yaml",
            )

        for cmd in cmd_deploy_workflow_api:

            result = run_subcommand(cmd=cmd.split())
            logger.debug(result)
            time.sleep(2)

    minio_version = "5.0.7"
    cmd_install_minio = [
        "helm",
        "install",
        "minio",
        "minio/minio",
        "--set",
        "resources.requests.memory=512Mi",
        "--set",
        "replicas=1",
        "--set",
        "persistence.enabled=true",
        "--set",
        "mode=standalone",
        "--set",
        "rootUser=rootuser",
        "--set",
        "rootPassword=rootpass123",
        f"--namespace={user_namespace}",
        "--create-namespace",
        f"--version={minio_version}"]

    result = subprocess.run(
        cmd_add_repo,
        check=True
    )

    logger.debug(result)

    result = subprocess.run(
        cmd_install_minio,
        check=True,
    )

    logger.debug(result)


@provisioner.get("/details/")
async def get_backend_credentials(consumer_id: str, db: Session = Depends(get_db)):

    consumer = crud.get_consumer_by_consumer_id(db=db,
                                                consumer_id=consumer_id)

    if not consumer:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="consumer_id not exist")

    base_url = f"http://{BACKEND_ENTRYPOINT}/{WF_API_ROOT_PATH}"

    api_details = schemas.WorkflowBackendDetails(
        url=f"{base_url}{consumer.workflow_backend_id}/docs",
        token=consumer.workflow_api_access_token)

    return api_details


@provisioner.post("/provision/static/")
async def static_provision(consumer_name: str,
                           db: Session = Depends(get_db)):

    workflow_backend_id = str(uuid.uuid4())
    logger.debug("do static provisioning")
    consumer = crud.get_consumer_by_consumer_id(db=db,
                                                consumer_id=consumer_name)

    access_token = str(uuid.uuid4())
    if WF_API_STATIC_ACCESS_TOKEN:
        access_token = WF_API_STATIC_ACCESS_TOKEN

    if not consumer:
        t = Thread(target=deploy_workflow_api,
                   kwargs={"workflow_backend_id": workflow_backend_id,
                           "workflow_api_access_token": access_token})
        t.start()

        consumer = crud.create_consumer(db=db,
                                        consumer=schemas.ConsumerCreate(
                                            id=consumer_name,
                                            workflow_backend_id=workflow_backend_id,
                                            access_token=access_token))
    return consumer


@provisioner.get("/provision/consumers")
async def get_consumers(db: Session = Depends(get_db)):

    consumers = crud.get_consumers(db=db)
    return consumers


@provisioner.post("/provision/")
async def provision(edc_request: HttpProvisionerRequest, db: Session = Depends(get_db)):
    """
    Process the provisioning the workflow-api for a service.
    Deploys the workflow-api for a user and registers a negotiated service.
    If the workflow-api is already deployed,
     - check if the requested service was already in usage, send access token back.
     - if the requested service was not in usage, add it to the allowed services and send access token back.
    """

    # logger.debug(await request.body())
    logger.debug("provisioner_request: %s", edc_request.json())

    logger.debug("do task")
    t = Thread(target=handle_edc_request,
               kwargs={"provisioner_request": edc_request, "db": db})
    t.start()

    return {}


@provisioner.post("/deprovision/{backend_id}")
async def do_deprovision(backend_id: str, db: Session = Depends(get_db)):
    """
    deprovisions the workflow-api and with it, all resources.
    """

    backend_uuid = uuid.UUID(backend_id,
                             version=4)

    if not crud.workflow_backend_exists(
            db=db,
            workflow_backend_id=backend_uuid):
        raise HTTPException(status_code=404, detail="Backend not exists")

    crud.delete_consumer_by_backend_id(
        db=db,
        workflow_backend_id=backend_uuid)

    cmd_delete_user_namespace = [
        "kubectl", "delete",
        "namespace", backend_id
    ]

    result = subprocess.run(
        cmd_delete_user_namespace,
        check=True,
    )

    logger.info(result)
