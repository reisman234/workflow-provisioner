REPOSITORY=harbor.gx4ki.imla.hs-offenburg.de
APPLICATION=gx4ki/workflow-provisioner:latest

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

	docker network connect imla-net workflow-provisioner --alias workflow-provisioner
	docker network connect minikube workflow-provisioner --alias workflow-provisioner

	docker start workflow-provisioner
	docker logs --follow workflow-provisioner
