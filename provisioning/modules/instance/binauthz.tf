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
  admission_whitelist_patterns {
    name_pattern = "quay.io/jetstack/*"
  }

  cluster_admission_rules {
    cluster                 = "${var.region}.${var.name}"
    evaluation_mode         = "REQUIRE_ATTESTATION"
    enforcement_mode        = "ENFORCED_BLOCK_AND_AUDIT_LOG"
    require_attestations_by = [var.binauthz_attestor_name]
  }
}
