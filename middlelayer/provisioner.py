"""
Provisioner module which is used by edc-connector.
Provisions the workflow-api for a requested service
"""
import logging
import subprocess
import sys


from fastapi import FastAPI


formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdout_handle = logging.StreamHandler(sys.stdout)
stdout_handle.setFormatter(formatter)
stderr_handle = logging.StreamHandler(sys.stderr)
stderr_handle.setFormatter(formatter)


logger = logging.getLogger("provisioner")
logger.setLevel(level=logging.DEBUG)
logger.addHandler(stdout_handle)

provisioner = FastAPI()


@provisioner.post("/provision")
async def do_provision():
    """
    process the provisioning the workflow-api for a service.
    """
    logger.debug("do_provision")

    # TODO
    # - check if workflow-api already for user provisioned

    user_name = "dummy-user"
    user_namespace = "dummy-namespace"

    cmd_add_repo = [
        "helm", "repo", "add", "minio", "https://charts.min.io/"
    ]

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
        "persistence.enabled=false",
        "--set",
        "mode=standalone",
        "--set",
        "rootUser=rootuser",
        "--set",
        "rootPassword=rootpass123",
        f"--namespace={user_namespace}",
        "--create-namespace",
        f"--version={minio_version}"]

    cmd = [
        "helm", "version"
    ]

    result = subprocess.run(
        cmd_add_repo,
        check=True
    )

    result = subprocess.run(
        cmd_install_minio,
        check=True,
    )

    logger.debug(result)


@provisioner.post("/deprovision")
async def do_deprovision():
    """
    deprovisions the workflow-api and with it all resources.
    """

    cmd_delete_user_namespace = [
        "kubectl", "delete",
        "namespace", "dummy-namespace"
    ]

    result = subprocess.run(
        cmd_delete_user_namespace,
        check=True,
    )

    logger.info(result)
