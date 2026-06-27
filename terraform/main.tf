terraform {
  required_version = ">= 1.6.0"

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

# Repository settings
resource "github_repository" "main" {
  name                        = var.github_repository
  description                 = "PyVista-like API for vtk.js"
  homepage_url                = "https://pyvista-js.readthedocs.io/en/latest/?badge=latest"
  visibility                  = "public"
  has_issues                  = true
  has_projects                = true
  has_wiki                    = true
  has_discussions             = true
  delete_branch_on_merge      = true
  allow_squash_merge          = true
  allow_merge_commit          = false
  allow_rebase_merge          = false
  allow_auto_merge            = false
  allow_update_branch         = true
  squash_merge_commit_title   = "PR_TITLE"
  squash_merge_commit_message = "BLANK"
  merge_commit_title          = "MERGE_MESSAGE"
  merge_commit_message        = "PR_TITLE"
  topics = [
    "3d",
    "fem",
    "finite-element-analysis",
    "finite-elements",
    "hacktoberfest",
    "mesh",
    "mesh-processing",
    "meshviewer",
    "open-science",
    "plotting",
    "python",
    "pyvista",
    "scientific-research",
    "scientific-visualization",
    "visualization",
    "vtk",
    "vtk-js",
  ]

  security_and_analysis {
    secret_scanning {
      status = "enabled"
    }
    secret_scanning_push_protection {
      status = "enabled"
    }
  }
}

# Dependabot security alerts
resource "github_repository_vulnerability_alerts" "main" {
  repository = github_repository.main.name
  enabled    = true
}

# Main ruleset: deletion, non-fast-forward, PR reviews, status checks
resource "github_repository_ruleset" "main" {
  repository  = github_repository.main.name
  name        = "main"
  target      = "branch"
  enforcement = "active"

  conditions {
    ref_name {
      include = ["refs/heads/main"]
      exclude = []
    }
  }

  rules {
    deletion         = true
    non_fast_forward = true

    pull_request {
      required_approving_review_count   = 0
      require_code_owner_review         = false
      dismiss_stale_reviews_on_push     = false
      require_last_push_approval        = false
      required_review_thread_resolution = false
      allowed_merge_methods = [
        "merge",
        "squash",
        "rebase",
      ]
    }

    required_status_checks {
      strict_required_status_checks_policy = true
      do_not_enforce_on_create             = false

      required_check {
        context        = "test (macos-latest, 3.12)"
        integration_id = 15368
      }
      required_check {
        context        = "test (macos-latest, 3.13)"
        integration_id = 15368
      }
      required_check {
        context        = "test (macos-latest, 3.14)"
        integration_id = 15368
      }
      required_check {
        context        = "test (ubuntu-latest, 3.12)"
        integration_id = 15368
      }
      required_check {
        context        = "test (ubuntu-latest, 3.13)"
        integration_id = 15368
      }
      required_check {
        context        = "test (ubuntu-latest, 3.14)"
        integration_id = 15368
      }
      required_check {
        context        = "test (windows-latest, 3.12)"
        integration_id = 15368
      }
      required_check {
        context        = "test (windows-latest, 3.13)"
        integration_id = 15368
      }
      required_check {
        context        = "test (windows-latest, 3.14)"
        integration_id = 15368
      }
      required_check {
        context = "docs/readthedocs.org:pyvista-js"
      }
      required_check {
        context = "docs/readthedocs.org:pyvista-js-ja"
      }
    }
  }
}
