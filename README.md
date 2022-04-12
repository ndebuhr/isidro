# Isidro (Chatbot)

Isidro includes:
* Connectors to Slack and Mattermost for event subscription and response
* Policy- and NLP-based workflow planning
* Automated execution of workflows (e.g., provisioning, deployments, and test execution)
* Automated presentation of data (e.g., deployment metrics, performance testing results, and spam trends)

## System installation

### Provision with Terraform

The following IAM permissions are required for provisioning.  Consider creating a custom Isidro Provisioner role:
1. binaryauthorization.attestors.create
1. binaryauthorization.attestors.delete
1. binaryauthorization.attestors.get
1. binaryauthorization.attestors.update
1. binaryauthorization.policy.get
1. binaryauthorization.policy.update
1. cloudkms.cryptoKeyVersions.create
1. cloudkms.cryptoKeyVersions.destroy
1. cloudkms.cryptoKeyVersions.get
1. cloudkms.cryptoKeyVersions.list
1. cloudkms.cryptoKeyVersions.restore
1. cloudkms.cryptoKeyVersions.update
1. cloudkms.cryptoKeyVersions.viewPublicKey
1. cloudkms.cryptoKeys.create
1. cloudkms.cryptoKeys.get
1. cloudkms.cryptoKeys.list
1. cloudkms.cryptoKeys.update
1. cloudkms.keyRings.create
1. cloudkms.keyRings.get
1. compute.instanceGroupManagers.get
1. compute.zones.list
1. container.clusters.create
1. container.clusters.delete
1. container.clusters.get
1. container.clusters.update
1. container.configMaps.create
1. container.configMaps.delete
1. container.configMaps.get
1. container.namespaces.create
1. container.namespaces.delete
1. container.namespaces.get
1. container.operations.get
1. containeranalysis.notes.create
1. containeranalysis.notes.delete
1. containeranalysis.notes.get
1. gkehub.memberships.create
1. gkehub.memberships.delete
1. gkehub.memberships.get
1. gkehub.operations.get
1. iam.serviceAccountKeys.create
1. iam.serviceAccountKeys.get
1. iam.serviceAccounts.create
1. iam.serviceAccounts.delete
1. iam.serviceAccounts.actAs
1. iam.serviceAccounts.get
1. iam.serviceAccounts.list
1. serviceusage.services.disable
1. serviceusage.services.enable
1. serviceusage.services.get
1. serviceusage.services.list
1. resourcemanager.projects.get
1. resourcemanager.projects.getIamPolicy
1. resourcemanager.projects.setIamPolicy

Bind the required permissions to an Isidro Provisioner service account, and export a service account key.  Set `GOOGLE_PROJECT` and `GOOGLE_APPLICATION_CREDENTIALS` environment variables.

Setup secondary IP ranges in the desired region (e.g., "gke-isidro-pods" and "gke-isidro-services"), then [run Terraform provisioning, with variable changes/overrides where required](provisioning/)
```bash
terraform init
terraform apply
    -var network=default \
    -var subnetwork=default \
    -var ip_range_pods="gke-isidro-pods" \
    -var ip_range_services="gke-isidro-services"
```

Configure kubectl to use the new cluster.  Create a namespace, if a non-default namespace is desired.

### Certbot (for TLS) preparation

1. In Google Cloud Platform, create a Cloud DNS zone for your domain
1. In your domain name registrar, ensure the domain nameservers are set to the values from Google
1. In Google Cloud Platform, create a role with the following permissions:
    1. dns.changes.create
    1. dns.changes.get
    1. dns.managedZones.list
    1. dns.resourceRecordSets.create
    1. dns.resourceRecordSets.delete
    1. dns.resourceRecordSets.list
    1. dns.resourceRecordSets.update
1. Create a new Isidro Certbot service account and assign the newly-recreated role

Generate a json key file for the service account.  Rename the file to `google.json`, then add it to Kubernetes as a secret:
```bash
kubectl create secret generic google-json --from-file google.json
```

### Istio ingress gateway

```bash
kubectl create namespace istio-ingressgateway
kubectl label namespace istio-ingressgateway istio.io/rev=asm-managed --overwrite
kubectl apply -f anthos-service-mesh-packages/samples/gateways/istio-ingressgateway -n istio-ingressgateway
```

### Enable cluster features

In the Google Cloud Console:
* Enable Anthos Service Mesh in "Anthos > Features"
* Enable Managed Prometheus for the provisioned cluster

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

Create a Slack App.  Enable and configure the event subscription feature.  

### Mattermost configuration
_Relevant if you are using Mattermost as your chat tool_

1. In the System Console, under "Integrations > Bot Accounts", "Enable Bot Account Creation"
1. In the Integrations portal, create a bot account with the name "isidro", role "System Administrator",, and the "post:all"
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

Create a personal access token, which includes `repo` and `workflow` permissions.  Use the token for the Helm value `deployer.github.token`.

## Usage

Mention @isidro in Slack messages, and get a response.  Use separate message threads for separate chatbot conversations.

### Test payload
```bash
curl -X POST https://example.com/api/v1/submit \
    -H "Content-Type: application/json" \
    -d '{"token": "1234567890", "event": {"channel": "quality", "ts": "1234567890", "user": "me", "text": "Hello"}}'
```

## Development

### Skaffold

1. Configure kubeconfig
1. Create a service account and bind the Cloud Build Service Account role
1. Generate a service account key for the new service account
1. Set `GOOGLE_PROJECT` and `GOOGLE_APPLICATION_CREDENTIALS`

```bash
cp skaffold.dev.yaml skaffold.yaml
sed -i "s/GOOGLE_PROJECT/$GOOGLE_PROJECT/g" skaffold.yaml
skaffold dev
```