#!/bin/sh

if [ -z "${KUBERNETES_SERVICE_HOST}" ] || [ -z "${KUBERNETES_SERVICE_PORT}" ]
then
    echo "incluster environment not set ... skip kubeconfig creation"
    return
fi

service_account_dir=/var/run/secrets/kubernetes.io/serviceaccount

if [ ! -f "${service_account_dir}/ca.crt" ] || [ ! -f "${service_account_dir}/token" ]
then
    echo "service account files not found ... skip kubeconfig creation"
    return
fi

CLUSTER_ENDPOINT=https://${KUBERNETES_SERVICE_HOST}:${KUBERNETES_SERVICE_PORT}
CLUSTER_CA_CERT=$(cat "${service_account_dir}/ca.crt" | base64 -w0)
SERVICE_ACCOUNT_TOKEN=$(cat "${service_account_dir}/token")

KUBECONFIG_FILE="~/.kube/config"

mkdir -p ~/.kube
cat << EOF > ${KUBECONFIG_FILE}
apiVersion: v1
clusters:
  - cluster:
      certificate-authority-data: ${CLUSTER_CA_CERT}
      server: ${CLUSTER_ENDPOINT}
    name: minikube
contexts:
  - context:
      cluster: minikube
      namespace: default
      user: workflow-provisioner-admin
    name: minikube
current-context: minikube
kind: Config
preferences: {}
users:
  - name: workflow-provisioner-admin
    user:
      token: ${SERVICE_ACCOUNT_TOKEN}
EOF

echo "kubeconfig file created at ${KUBECONFIG_FILE}"
