terraform {
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }
}

provider "github" {
  token = var.github_token
  owner = var.github_owner
}

# Branch protection on main
resource "github_branch_protection" "main" {
  repository_id  = var.github_repository
  pattern        = var.branch_name
  enforce_admins = true

  required_pull_request_reviews {
    require_code_owner_reviews = true
  }

  required_status_checks {
    strict   = true
    contexts = ["lint", "js-check", "test"]
  }
}

# Require conversation resolution
resource "github_repository_ruleset" "conversation_resolution" {
  repository  = var.github_repository
  name        = "Require conversation resolution on main"
  target      = "branch"
  enforcement = "active"

  conditions {
    ref_name {
      include = ["refs/heads/main"]
      exclude = []
    }
  }

  rules {
    pull_request {
      required_review_thread_resolution = true
    }
  }
}
