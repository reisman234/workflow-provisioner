REPOSITORY=
APPLICATION=imlahso/workflow-provisioner:latest

NAMESPACE=workflow-provisioner-demo

all:
	echo "use specific targets"

image:
	docker build -t ${REPOSITORY}${APPLICATION} .

publish:
	docker build --pull --no-cache -t ${REPOSITORY}${APPLICATION} .
	docker push ${REPOSITORY}${APPLICATION}


delete-demo-config:
	kubectl delete namespace ${NAMESPACE}

demo-config:
	cp config/.kube/config.tmpl config/.kube/config
	kubectl create namespace ${NAMESPACE}

	cat manifests/provisioner-serviceaccount.yaml | sed  "s/namespace: workflow-provisioner/namespace: ${NAMESPACE}/g" | kubectl -n ${NAMESPACE} apply -f -

	kubectl cluster-info | grep "control plane" | grep -oP '(?=https://).*(?<=:(6|8)443)' | xargs -i sed -i "s|\[CLUSTER_ENDPOINT\]|{}|" config/.kube/config
	kubectl -n ${NAMESPACE} get secrets workflow-provisioner-token -o json | jq -r '.data."ca.crt"' | xargs -i sed -i "s|\[CLUSTER_CA_CERT\]|{}|" config/.kube/config
	kubectl -n ${NAMESPACE} get secrets workflow-provisioner-token -o json | jq -r .data.token | base64 -d | xargs -i sed -i "s|\[SERVICE_ACCOUNT_TOKEN\]|{}|" config/.kube/config
