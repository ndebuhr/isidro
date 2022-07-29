---
title: "Setup"
date: 2022-05-25T16:55:46+03:00
draft: false
menu:
  main:
    pre: "/icons/usage.svg"
    title: "Setup"
    identifier: "Setup"
    weight: 2
---

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

Set the `GOOGLE_PROJECT`, `ISIDRO_DOMAIN`, `MATTERMOST_DOMAIN`, and `DNS_ZONE_NAME` environment variables, with something like:
```bash
export GOOGLE_PROJECT=example
export ISIDRO_DOMAIN=isidro.example.com
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
```

Navigate to the [development](provisioning/dev/) or [production](provisioning/prod/) directory, then set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable, with something like:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=../../isidro-provisioner.json
```

Run Terraform provisioning, with something like:
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
```

Add helm repositories:
```bash
helm repo add mattermost https://helm.mattermost.com
helm repo add jetstack https://charts.jetstack.io
```

Setup skaffold credentials:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=isidro-skaffold.json
```

### Development environments

Hydrate configurations:
```bash
cp skaffold.dev.yaml skaffold.yaml
sed -i "s/GOOGLE_PROJECT/$GOOGLE_PROJECT/g" skaffold.yaml
sed -i "s/MATTERMOST_DOMAIN/$MATTERMOST_DOMAIN/g" skaffold.yaml
sed -i "s/ISIDRO_DOMAIN/$ISIDRO_DOMAIN/g" skaffold.yaml
sed -i "s/DNS_ZONE_NAME/$DNS_ZONE_NAME/g" skaffold.yaml

cp vendor/configconnector-setup.dev.yaml vendor/configconnector-setup.yaml
sed -i "s/GOOGLE_PROJECT/$GOOGLE_PROJECT/g" vendor/configconnector-setup.yaml
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
sed -i "s/ISIDRO_DOMAIN/$ISIDRO_DOMAIN/g" skaffold.yaml
sed -i "s/DNS_ZONE_NAME/$DNS_ZONE_NAME/g" skaffold.yaml

cp vendor/configconnector-setup.dev.yaml vendor/configconnector-setup.yaml
sed -i "s/GOOGLE_PROJECT/$GOOGLE_PROJECT/g" vendor/configconnector-setup.yaml
```

Make any required `skaffold.yaml` configuration changes, then run skaffold:
```bash
skaffold run
```

To teardown:
```bash
skaffold delete
```