FROM python:3.8-alpine

WORKDIR /root/


RUN apk update && apk add curl \
    && curl -LO https://dl.k8s.io/release/v1.22.0/bin/linux/amd64/kubectl \
    && chmod 0755 kubectl && mv kubectl /usr/local/bin
# install helm
RUN curl -LO https://get.helm.sh/helm-v3.11.2-linux-amd64.tar.gz \
    && tar -zxvf helm-v3.11.2-linux-amd64.tar.gz \
    && mv linux-amd64/helm /usr/local/bin/ \
    && rm -r linux-amd64 helm-v3.11.2-linux-amd64.tar.gz


WORKDIR /opt/
# python environment
COPY requirements.txt requirements.txt
COPY entrypoint.sh entrypoint.sh
RUN python -m venv .venv \
    && source .venv/bin/activate \
    && pip install -r requirements.txt

COPY middlelayer ./middlelayer

CMD ["/bin/sh", "entrypoint.sh"]
