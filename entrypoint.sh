#/bin/sh

source .venv/bin/activate

uvicorn middlelayer.provisioner:provisioner --host=0.0.0.0 --port=8888
