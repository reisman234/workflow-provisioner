# Workflow Provisioner

This Repository contains the implementation of a HTTP-Provisioner for an EDC-Connector, which deploys a Workflow-Controller into a running K8s-Cluster.
After the deployment the access information can be retrieved.

## Prerequisite

- having edc connectors with the required extensions and config ready
  - provisioner extension
- running k8s
  - use the [local setup](./docs/setup.md) guide to prepare a local minikube.

## Container Setup

At the moment, scripts and the image is designend to run a separately in it's container.
The following shows a overiew of this local demo setup.

![Workflow Provider](docs/workflow-provisioner.drawio.png)

After the cluster and connectors are prepared, run the workflow-provisioner container with the `test-run` target in the provided Makefile.
It creates a container and connects it to expected networks for the minikube cluster and the edc-connectors

```
make test-run
```

After everything is running, the connectors can make their contract negotiation phase, which will in the end trigger provisioning process.
