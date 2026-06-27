# Terraform Branch Protection

This directory contains Terraform configuration to manage branch protection
rules on the `main` branch as infrastructure-as-code.

## Resources

- `github_repository.main` — repository settings (description, topics, merge
  strategy, security & analysis).
- `github_repository_vulnerability_alerts.main` — enables Dependabot security
  alerts.
- `github_repository_ruleset.main` — enforces deletion and non-fast-forward
  protection, requires pull request reviews (0 approving reviews), and
  requires status checks (`test` matrix, Read the Docs builds) on `main`.

## Usage

```bash
cd terraform
terraform init
terraform plan -var="github_token=<your-token>"
terraform apply -var="github_token=<your-token>"
```

## Linting

The Terraform configuration is linted with [tflint](https://github.com/terraform-linters/tflint)
using the bundled Terraform Language ruleset with all rules enabled.
The configuration lives in `.tflint.hcl` in this directory.

tflint runs in CI via the `TFLint` GitHub Actions workflow on every change
to the `terraform/` directory. To run it manually:

```bash
cd terraform
tflint -f compact
```

## Variables

| Name | Description | Default |
| ----------------- | ---------------------------------------------------- | ------------- |
| `github_token` | GitHub personal access token with `repo:admin` scope | _(required)_ |
| `github_owner` | GitHub repository owner | `tkoyama010` |
| `github_repository` | GitHub repository name | `pyvista-js` |
