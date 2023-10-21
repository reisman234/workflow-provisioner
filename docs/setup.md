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

## Prepare kubeconfig

To be able to communicate with the k8s-api the provisioner requires a service account.
To setup everything in the k8s-cluster use the `demo-config` target from the makefile.

It creates a namespace, deploys RBAC rules, serviceaccount and tokens.
In a last step it creates the kubeconfig from a [template](../config/.kube/config.tmpl) and replaces the placeholders.
