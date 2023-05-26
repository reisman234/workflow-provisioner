https://devopscube.com/kubernetes-kubeconfig-file/

## create provisioner gx4ki-clusterrolebinding

**TODO** create proper clusterrole for binding

```shell
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
  name: gxk4i-provisioner-admin
  namespace: kube-system
EOF
```

### create ServiceAccount

```shell
kubectl --namespace kube-system create serviceaccount gxk4i-provisioner-admin
```

## set token in kubeconfig file

**Note:** Token has to be decoded
```shell
kubectl -n kube-system get secrets gxk4i-provisioner-admin-token-8rfxg -o yaml | yq  -r .data.token | base64 -d
```
