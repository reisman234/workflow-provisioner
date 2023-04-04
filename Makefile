REPOSITORY=harbor.gx4ki.imla.hs-offenburg.de
APPLICATION=gx4ki/workflow-provisioner:latest

all:
	echo "use specific targets"

image:
	docker build -t ${REPOSITORY}/${APPLICATION} .

publish:
	docker build --pull --no-cache -t ${REPOSITORY}/${APPLICATION} .
	docker push ${REPOSITORY}/${APPLICATION}