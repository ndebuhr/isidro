FROM almir/webhook:2.8.0

# apk install system prerequisite packages
RUN apk add --no-cache bash curl python

# install gcloud cli
RUN curl -sSL https://sdk.cloud.google.com | bash
ENV PATH $PATH:/root/google-cloud-sdk/bin

ADD hooks.yaml /etc/webhook/hooks.yaml
ADD pass.sh /var/webhook/pass.sh

EXPOSE 9000

ENTRYPOINT webhook -verbose -hooks /etc/webhook/hooks.yaml