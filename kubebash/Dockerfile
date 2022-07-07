FROM almir/webhook:2.8.0

# apk install system prerequisite packages
RUN apk add --no-cache curl

# install kubectl, kubeadm, and kubelet
RUN RELEASE="$(curl -sSL https://dl.k8s.io/release/stable.txt)" && \
    curl -L --remote-name-all "https://storage.googleapis.com/kubernetes-release/release/${RELEASE}/bin/linux/amd64/{kubeadm,kubelet,kubectl}" && \
    install kubeadm /usr/local/bin/ && \
    install kubelet /usr/local/bin/ && \
    install kubectl /usr/local/bin/ && \
    rm kubeadm kubelet kubectl

ADD hooks.yaml /etc/webhook/hooks.yaml
ADD pass.sh /var/webhook/pass.sh

EXPOSE 9000

ENTRYPOINT webhook -verbose -hooks /etc/webhook/hooks.yaml