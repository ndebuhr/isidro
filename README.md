# Isidro (Chatbot)

> Isidro is an Anthos- and GKE-based microservices chatbot

Isidro includes:
* Prebuilt connectors to Slack and Mattermost for event subscription and response
* Flexible, policy-based workflow planning
* Layered intent classification: BERT → ngrams-based regression → non-ML NLP techniques
* Easy delegation of build and deploy workflows to Jenkins, Cloud Build, and GitHub Actions
* Automated execution of workflows (e.g., provisioning, deployments, and test execution)
* Automated presentation of data (e.g., deployment metrics, performance testing results, and spam trends)
* Well-established paths for both development and production deployments
    * DEV: 2 clusters, 2 regions, 5 zones, and a regional Cloud Spanner instance
    * PROD: 6 clusters, 6 regions, 13 zones, and a multi-regional Cloud Spanner instance
* Security features like binary authorization, mTLS, workload identity, and network policies

![Isidro Map](images/isidro-map.png)

## Prerequisites
1. APIs and features enabled on Google Cloud Platform:
    1. API: Anthos
    1. API: Anthos Service Mesh Certificate Authority
    1. API: Binary Authorization
    1. API: Cloud KMS
    1. API: Cloud Resource Manager
    1. API: GKE Hub
    1. API: Kubernetes Engine
    1. API: Multi Cluster Ingress
    1. API: Multi-Cluster Service Discovery
    1. API: Traffic Director
    ```bash
    gcloud services enable \
        anthos.googleapis.com \
        binaryauthorization.googleapis.com \
        cloudkms.googleapis.com \
        cloudresourcemanager.googleapis.com \
        container.googleapis.com \
        gkehub.googleapis.com \
        redis.googleapis.com \
        meshca.googleapis.com \
        multiclusteringress.googleapis.com \
        multiclusterservicediscovery.googleapis.com \
        spanner.googleapis.com \
        trafficdirector.googleapis.com
    ```
    1. Anthos Feature: Service Mesh
1. A domain or subdomain managed through Google Cloud DNS
1. [Skaffold](https://skaffold.dev/) CLI v1.39+

## System installation
_While installation is possible using non-Linux clients, it's not a well-established or documented process_

### Provision with Terraform

Set the `GOOGLE_PROJECT`, `API_DOMAIN`, `MATTERMOST_DOMAIN`, and `DNS_ZONE_NAME` environment variables, with something like:
```bash
export GOOGLE_PROJECT=example
export API_DOMAIN=api.example.com
export MATTERMOST_DOMAIN=mattermost.example.com
export DNS_ZONE_NAME="example-com"
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
export GOOGLE_APPLICATION_CREDENTIALS=$PWD/isidro-provisioner.json
```

Navigate to the [development](provisioning/dev/) or [production](provisioning/prod/) directory and run Terraform provisioning, with something like:
```bash
gcloud init
terraform init
terraform apply
```

Create kubecontext configurations for the provisioned clusters:
```bash
# For development setups
gcloud container clusters get-credentials isidro-us --region us-central1
gcloud container clusters get-credentials isidro-config --region northamerica-northeast1
kubectl config rename-context gke_"$GOOGLE_PROJECT"_us-central1_isidro-us isidro-us
kubectl config rename-context gke_"$GOOGLE_PROJECT"_northamerica-northeast1_isidro-config isidro-config
```

```bash
# For production setups
gcloud container clusters get-credentials isidro-us-ia --region us-central1
gcloud container clusters get-credentials isidro-us-sc --region us-east1
gcloud container clusters get-credentials isidro-be --region europe-west1
gcloud container clusters get-credentials isidro-nl --region europe-west4
gcloud container clusters get-credentials isidro-tw --region asia-east1
gcloud container clusters get-credentials isidro-config --region northamerica-northeast1
kubectl config rename-context gke_"$GOOGLE_PROJECT"_us-central1_isidro-us-ia isidro-us-ia
kubectl config rename-context gke_"$GOOGLE_PROJECT"_us-east1_isidro-us-sc isidro-us-sc
kubectl config rename-context gke_"$GOOGLE_PROJECT"_europe-west1_isidro-be isidro-be
kubectl config rename-context gke_"$GOOGLE_PROJECT"_europe-west4_isidro-nl isidro-nl
kubectl config rename-context gke_"$GOOGLE_PROJECT"_asia-east1_isidro-tw isidro-tw
kubectl config rename-context gke_"$GOOGLE_PROJECT"_northamerica-northeast1 isidro-config
```

## Installation

Setup a service account for building the required artifacts:
```bash
gcloud iam service-accounts create isidro-skaffold \
    --display-name="Isidro Skaffold"
gcloud projects add-iam-policy-binding $GOOGLE_PROJECT \
    --member="serviceAccount:isidro-skaffold@$GOOGLE_PROJECT.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.builder"
gcloud iam service-accounts keys create isidro-skaffold.json \
    --iam-account="isidro-skaffold@$GOOGLE_PROJECT.iam.gserviceaccount.com"
export GOOGLE_APPLICATION_CREDENTIALS=$PWD/isidro-skaffold.json
```

Add helm repositories:
```bash
helm repo add mattermost https://helm.mattermost.com
helm repo add jetstack https://charts.jetstack.io
```

### Development environments

Hydrate configurations:
```bash
cp skaffold.dev.yaml skaffold.yaml
sed -i "s/GOOGLE_PROJECT/$GOOGLE_PROJECT/g" skaffold.yaml
sed -i "s/MATTERMOST_DOMAIN/$MATTERMOST_DOMAIN/g" skaffold.yaml
sed -i "s/API_DOMAIN/$API_DOMAIN/g" skaffold.yaml
sed -i "s/DNS_ZONE_NAME/$DNS_ZONE_NAME/g" skaffold.yaml
```

Make any required `skaffold.yaml` configuration changes, then run skaffold:
```bash
skaffold dev
```

### Production environments

Hydrate confiigurations:
```bash
cp skaffold.prod.yaml skaffold.yaml
sed -i "s/GOOGLE_PROJECT/$GOOGLE_PROJECT/g" skaffold.yaml
sed -i "s/MATTERMOST_DOMAIN/$MATTERMOST_DOMAIN/g" skaffold.yaml
sed -i "s/API_DOMAIN/$API_DOMAIN/g" skaffold.yaml
sed -i "s/DNS_ZONE_NAME/$DNS_ZONE_NAME/g" skaffold.yaml
```

Make any required `skaffold.yaml` configuration changes, then run skaffold:
```bash
skaffold run
```

To teardown:
```bash
skaffold delete
```

## Deprovisioning

In the Terraform provisioning directory, run:
```bash
gcloud init
terraform destroy
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
    1. Callback URL is https://api.example.com/v1/submit (replace api.example.com with your Isidro API domain)
    1. Leave the remaining values as the defaults
1. Copy the verification token to the Helm values (or Skaffold overrides) as `mattermost.verificationToken`
1. Upgrade the Helm installation

### GitHub Actions
_Relevant if you are triggering GitHub Actions workflows with the chatbot_

Create a personal access token, which includes `repo`, `workflow`, and `packages` permissions.  Use the token for the Helm value `deployer.github.token`.

## Usage

Mention @isidro in Slack messages, and get a response.  Use separate message threads for separate chatbot conversations.

### Test payload
```bash
curl -X POST https://api.example.com/v1/submit \
    -H "Content-Type: application/json" \
    -d '{"token": "1234567890", "event": {"channel": "quality", "ts": "1234567890", "user": "me", "text": "Hello"}}'
```