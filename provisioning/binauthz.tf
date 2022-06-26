resource "google_binary_authorization_policy" "isidro" {
  global_policy_evaluation_mode = "ENABLE"

  default_admission_rule {
    evaluation_mode  = "ALWAYS_ALLOW"
    enforcement_mode = "ENFORCED_BLOCK_AND_AUDIT_LOG"
  }

  admission_whitelist_patterns {
    name_pattern = "mysql:*"
  }
  admission_whitelist_patterns {
    name_pattern = "mattermost/mattermost-team-edition:*"
  }
  admission_whitelist_patterns {
    name_pattern = "openpolicyagent/opa:*"
  }
  admission_whitelist_patterns {
    name_pattern = "docker.io/bitnami/kubectl:*"
  }
  admission_whitelist_patterns {
    name_pattern = "docker.io/bitnami/mongodb:*"
  }
  admission_whitelist_patterns {
    name_pattern = "docker.io/bitnami/rabbitmq:*"
  }
  admission_whitelist_patterns {
    name_pattern = "docker.io/bitnami/redis:*"
  }

  cluster_admission_rules {
    cluster                 = "${var.primary_cluster_region}.${var.primary_cluster_name}"
    evaluation_mode         = "REQUIRE_ATTESTATION"
    enforcement_mode        = "ENFORCED_BLOCK_AND_AUDIT_LOG"
    require_attestations_by = [google_binary_authorization_attestor.isidro.name]
  }

  cluster_admission_rules {
    cluster                 = "${var.secondary_cluster_region}.${var.secondary_cluster_name}"
    evaluation_mode         = "REQUIRE_ATTESTATION"
    enforcement_mode        = "ENFORCED_BLOCK_AND_AUDIT_LOG"
    require_attestations_by = [google_binary_authorization_attestor.isidro.name]
  }
}

resource "google_container_analysis_note" "isidro" {
  name = "isidro-attestor-note"
  attestation_authority {
    hint {
      human_readable_name = "Isidro deployment attestation"
    }
  }
}

resource "google_binary_authorization_attestor" "isidro" {
  name = "isidro-attestor"
  attestation_authority_note {
    note_reference = google_container_analysis_note.isidro.name
    public_keys {
      id = data.google_kms_crypto_key_version.isidro.id
      pkix_public_key {
        public_key_pem      = data.google_kms_crypto_key_version.isidro.public_key[0].pem
        signature_algorithm = data.google_kms_crypto_key_version.isidro.public_key[0].algorithm
      }
    }
  }
}

resource "random_string" "keyring_suffix" {
  length   = 8
  upper    = false
  lower    = true
  numeric  = false
  special  = false
}

resource "google_kms_key_ring" "isidro" {
  name     = "isidro-${random_string.keyring_suffix.result}"
  location = "global"
}

resource "google_kms_crypto_key" "isidro" {
  name     = "isidro-binauthz-attestation"
  key_ring = google_kms_key_ring.isidro.id
  purpose  = "ASYMMETRIC_SIGN"

  version_template {
    algorithm = "EC_SIGN_P384_SHA384"
  }
}

data "google_kms_crypto_key_version" "isidro" {
  crypto_key = google_kms_crypto_key.isidro.id
}