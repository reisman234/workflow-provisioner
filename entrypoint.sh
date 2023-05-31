#/bin/sh

source .venv/bin/activate

source ./create-kubeconfig.inc

uvicorn middlelayer.provisioner:provisioner --host=0.0.0.0 --port=8888
