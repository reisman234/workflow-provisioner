# Setup

## Development/Test Setup

A minikube environment is used for local development.
To reach the deployed workflow-controller, the ingress addon must be enabled.

```bash
minikube start
minikube addons enable ingress
```

Be sure that the container images available in your registry and the image reference is adapted in the docker-compose or deployment files.
Or build the images directly into the minikube cluster, without needing a registry.

```bash
eval $(minikube docker-env)
make image
```

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
# create service account token
cat << EOF | kubectl -n gx4ki-workflow-provisioner apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: gx4ki-provisioner-admin-token
  annotations:
    kubernetes.io/service-account.name: gx4ki-provisioner-admin
type: kubernetes.io/service-account-token
EOF

```

### Prepare the kubeconfig file

Manually create the kubeconfig file, use the template `config/.kube/config.tmpl` for help.

```bash
cp config/.kube/config.tmpl config/.kube/config
```

Collect the required information to fill out the missing pieces, `CLUSTER_CA_CERT`, `CLUSTER_ENDPOINT`, and `CLUSTER_TOKEN`.

```bash
# ca.crt: default location= ~/.minikube/ca.crt
# CLUSTER_CA_CERT
cat ~/.minikube/ca.crt | base64 -w0

# k8s-api ip and port for minikube
# if not already started and connected to your minikube:
# minkube start
# CLUSTER_ENDPOINT:
kubectl cluster-info | grep "control plane" | grep -o "https.*$"

# find and get the secret for the service account, show the token
# CLUSTER_TOKEN
kubectl -n gx4ki-workflow-provisioner get secrets gx4ki-provisioner-admin-token -o jsonpath={.data.token} |\
base64 -d
```
