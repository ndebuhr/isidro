FROM almir/webhook:2.8.0

# apk install system prerequisite packages
RUN apk add --no-cache bash curl jq python3

# install gcloud cli
RUN curl -sSL https://sdk.cloud.google.com | bash
ENV PATH $PATH:/root/google-cloud-sdk/bin
RUN gcloud components install beta

ADD hooks.async.yaml /etc/webhook/hooks.async.yaml
ADD hooks.sync.yaml /etc/webhook/hooks.sync.yaml
ADD pass.sh /var/webhook/pass.sh

EXPOSE 9000