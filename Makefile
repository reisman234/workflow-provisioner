REPOSITORY=harbor.gx4ki.imla.hs-offenburg.de
APPLICATION=gx4ki/workflow-provisioner:latest

NAMESPACE=workflow-provisioner-demo

all:
	echo "use specific targets"

image:
	docker build -t ${REPOSITORY}/${APPLICATION} .

publish:
	docker build --pull --no-cache -t ${REPOSITORY}/${APPLICATION} .
	docker push ${REPOSITORY}/${APPLICATION}

test-run:
	docker rm -f workflow-provisioner
	docker create  --rm --name workflow-provisioner \
	-v ./config/.kube:/root/.kube \
	-v ./database/:/opt/database \
	-v ./k8s/secrets/:/opt/k8s/secrets \
	${REPOSITORY}/${APPLICATION}

	docker network connect edc-net workflow-provisioner --alias workflow-provisioner
	docker network connect minikube workflow-provisioner --alias workflow-provisioner

	docker start workflow-provisioner
	docker logs --follow workflow-provisioner

delete-demo-config:
	kubectl delete namespace ${NAMESPACE}

demo-config:
	cp config/.kube/config.tmpl config/.kube/config
	kubectl create namespace ${NAMESPACE}

	cat manifests/provisioner-serviceaccount.yaml | sed  "s/namespace: workflow-provisioner/namespace: ${NAMESPACE}/g" | kubectl -n ${NAMESPACE} apply -f -

	kubectl cluster-info | grep "control plane" | grep -oP '(?=https://).*(?<=:(6|8)443)' | xargs -i sed -i "s|\[CLUSTER_ENDPOINT\]|{}|" config/.kube/config
	kubectl -n ${NAMESPACE} get secrets workflow-provisioner-token -o json | jq -r '.data."ca.crt"' | xargs -i sed -i "s|\[CLUSTER_CA_CERT\]|{}|" config/.kube/config
	kubectl -n ${NAMESPACE} get secrets workflow-provisioner-token -o json | jq -r .data.token | base64 -d | xargs -i sed -i "s|\[SERVICE_ACCOUNT_TOKEN\]|{}|" config/.kube/config
