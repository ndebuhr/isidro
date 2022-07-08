#!/usr/bin/env bash

set -e

cd provisioning/$1
KEYRING=$(terraform output --raw binauthz_keyring)
KEYRING_LOCATION=$(terraform output --raw binauthz_keyring_location)
ATTESTOR=$(terraform output --raw binauthz_attestor)
KEY=$(terraform output --raw binauthz_key)
cd ../..

DIGEST=$(gcloud container images describe $2 \
    --format='get(image_summary.fully_qualified_digest)')

gcloud beta container binauthz attestations sign-and-create \
    --artifact-url="$DIGEST" \
    --attestor="$ATTESTOR" \
    --attestor-project="$GOOGLE_PROJECT" \
    --keyversion-project="$GOOGLE_PROJECT" \
    --keyversion-location="$KEYRING_LOCATION" \
    --keyversion-keyring="$KEYRING" \
    --keyversion-key="$KEY" \
    --keyversion="1"