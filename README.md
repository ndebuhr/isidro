# Isidro (Chatbot)

Isidro includes:
* Connectors to Slack and Mattermost for event subscription and response
* Policy- and NLP-based workflow planning
* Automated execution of workflows (e.g., provisioning, deployments, and test execution)
* Automated presentation of data (e.g., deployment metrics, performance testing results, and spam trends)

## Prerequisites
1. Willingness and ability to run the system on Google Cloud Platform (other cloud providers are possible, but would require some hacking)
1. A domain or subdomain managed through Google Cloud DNS

## System installation
_While installation is possible using non-Linux clients, it's not a well-established or documented process_

### Provision with Terraform

Set the `GOOGLE_PROJECT` environment variable, with something like:
```bash
export GOOGLE_PROJECT=example
```

Create a service account for provisioning the required resources:
```bash
gcloud iam roles create isidro_provisioner \
    --project=$GOOGLE_PROJECT \
    --file=roles/provisioner.yaml
gcloud iam service-accounts create isidro-provisioner \
    --display-name="Isidro Provisioner"
gcloud projects add-iam-policy-binding $GOOGLE_PROJECT \
    --member="serviceAccount:isidro-provisioner@$GOOGLE_PROJECT.iam.gserviceaccount.com" \
    --role="projects/$GOOGLE_PROJECT/roles/isidro_provisioner"
gcloud iam service-accounts keys create isidro-provisioner.json \
    --iam-account="isidro-provisioner@$GOOGLE_PROJECT.iam.gserviceaccount.com"
```

Navigate to the [provisioning/](provisioning/) directory, then set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable, with something like:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=../isidro-provisioner.json
```

Enable the following APIs and features in GCP:
1. API: Binary Authorization
1. API: Cloud KMS
1. API: Google Kubernetes Engine
1. API: Anthos
1. Anthos Feature: Service Mesh

Setup secondary IP ranges in the desired region and subnet (e.g., "gke-isidro-pods" and "gke-isidro-services"), then [run Terraform provisioning, with variable changes/overrides where required](provisioning/).  Something like:
```bash
terraform init
terraform apply \
    -var network=default \
    -var subnetwork=default \
    -var ip_range_pods="gke-isidro-pods" \
    -var ip_range_services="gke-isidro-services"
```

Configure kubectl to use the new cluster.  Create a namespace, if a non-default namespace is desired.

### Certbot (for TLS) preparation

Create a service account for provisioning the required resources:
```bash
gcloud iam roles create isidro_certbot \
    --project=$GOOGLE_PROJECT \
    --file=roles/certbot.yaml
gcloud iam service-accounts create isidro-certbot \
    --display-name="Isidro Certbot"
gcloud projects add-iam-policy-binding $GOOGLE_PROJECT \
    --member="serviceAccount:isidro-certbot@$GOOGLE_PROJECT.iam.gserviceaccount.com" \
    --role="projects/$GOOGLE_PROJECT/roles/isidro_certbot"
gcloud iam service-accounts keys create isidro-certbot.json \
    --iam-account="isidro-certbot@$GOOGLE_PROJECT.iam.gserviceaccount.com"
```

Add the service account key to Kubernetes as a secret:
```bash
kubectl create secret generic isidro-certbot-key --from-file isidro-certbot.json
```

### Istio ingress gateway

```bash
kubectl create namespace istio-ingressgateway
kubectl label namespace istio-ingressgateway istio.io/rev=asm-managed --overwrite
kubectl apply -f anthos-service-mesh-packages/samples/gateways/istio-ingressgateway -n istio-ingressgateway
```

### Enable GMP

In the Google Cloud Console, enable Managed Prometheus for the provisioned cluster

### Helm installation

```bash
cd chart
helm install isidro .
```

### DNS setup

Setup an A record DNS entry for the Istio Ingress Gateway Load Balancer IP
```bash
kubectl get svc -n istio-ingressgateway
```

## System configuration

### Slack configuration
_Relevant if you are using Slack as your chat tool_

Create a Slack app:
1. Update the [example Slack manifest](slack/manifest.yaml) to use your Isidro endpoint
1. Create a Slack app using the application manifest
1. Consider giving the app a profile picture (e.g., the Terminator)
1. Use the verification token, under the app's "Basic Information" for Helm value `slack.verificationToken`
1. Use the OAuth token, under the app's "OAuth & Permissions" for Helm value `slack.oauthToken`

### Mattermost configuration
_Relevant if you are using Mattermost as your chat tool_

1. In the System Console, under "Integrations > Bot Accounts", "Enable Bot Account Creation"
1. In the Integrations portal, create a bot account with the name "isidro" and role "System Administrator"
    1. Consider giving the app a profile picture (e.g., the Terminator)
1. Copy the access token to the Helm values (or Skaffold overrides) as `mattermost.accessToken`
1. Add an outgoing webhook:
    1. Recommended title is "Isidro Mentions"
    1. Recommended description is "Push notification enabling the Isidro chatbot to respond to @mentions"
    1. Application type is "application/json"
    1. Trigger word is "@isidro"
    1. Callback URL is https://example.com/isidro/api/v1/submit (replace example.com with your domain)
    1. Leave the remaining values as the defaults
1. Copy the verification token to the Helm values (or Skaffold overrides) as `mattermost.verificationToken`
1. Upgrade the Helm installation

### GitHub Actions
_Relevant if you are triggering GitHub Actions workflows with the chatbot_

Create a personal access token, which includes `repo`, `workflow`, and `packages` permissions.  Use the token for the Helm value `deployer.github.token`.

## Usage

Mention @isidro in Slack messages, and get a response.  Use separate message threads for separate chatbot conversations.

## Development

### Skaffold

Set the `GOOGLE_PROJECT` environment variable and configure kubeconfig to use the isidro cluster.

Setup a service account with the Cloud Build Service Account Role:
```bash
gcloud iam service-accounts create isidro-skaffold \
    --display-name="Isidro Skaffold"
gcloud projects add-iam-policy-binding $GOOGLE_PROJECT \
    --member="serviceAccount:isidro-skaffold@$GOOGLE_PROJECT.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.builder"
gcloud iam service-accounts keys create isidro-skaffold.json \
    --iam-account="isidro-skaffold@$GOOGLE_PROJECT.iam.gserviceaccount.com"
```

Setup skaffold files and credentials:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=isidro-skaffold.json
cp skaffold.dev.yaml skaffold.yaml
sed -i "s/GOOGLE_PROJECT/$GOOGLE_PROJECT/g" skaffold.yaml
```

Make any required `skaffold.yaml` configuration changes, then run skaffold:
```bash
skaffold dev
```

#### Skaffold-based persistent deployment

To setup:
```bash
skaffold run
```

To teardown:
```bash
skaffold delete
```

### Test payload
```bash
curl -X POST https://example.com/api/v1/submit \
    -H "Content-Type: application/json" \
    -d '{"token": "1234567890", "event": {"channel": "quality", "ts": "1234567890", "user": "me", "text": "Hello"}}'
```