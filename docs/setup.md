# Setup

## Development

A minikube environment is used for local development.

### Create the ServiceAccount for the Provisioner Service and receive the token.
```bash
kubectl create namespace gx4ki-workflow-provisioner

# TODO create specific ClusterRole which has only the rules which are required.
cat << EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: gx4ki-provisioner-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: gx4ki-provisioner-admin
  namespace: gx4ki-workflow-provisioner
EOF

kubectl -n gx4ki-workflow-provisioner create serviceaccount gx4ki-provisioner-admin
```

### Prepare the kubeconfig file
```bash
cp config/.kube/config.tmpl config/.kube/config
# provide the required information to connect to the minikube cluster

# ca.crt: default location= ~/.minikube/ca.crt
CLUSTER_CA_CERT=$(cat ~/.minikube/ca.crt | base64 -w0)
# k8s-api ip and port for minikube
minkube start
kubectl cluster-info
CLUSTER_ENDPOINT="https://192.168.49.2:8443"

# find and get the secret for the service account, show the token
CLUSTER_TOKEN=$(kubectl -n gx4ki-workflow-provisioner get serviceaccounts gx4ki-provisioner-admin -o jsonpath={.secrets[].name} |\
xargs -i kubectl -n gx4ki-workflow-provisioner get secret {} -o jsonpath={.data.token} |\
base64 -d)
```

### Build the Image

```bash
# to build the image for the minikube environment run first eval $(minikube docker-env)
make image
```
