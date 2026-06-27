# Terraform Branch Protection

This directory contains Terraform configuration to manage branch protection
rules on the `main` branch as infrastructure-as-code.

## Resources

- `github_branch_protection.main` — requires a pull request with code owner
  review, enforces status checks (`lint`, `js-check`, `test`), keeps the branch
  up to date before merging, and restricts direct pushes (admins included).
- `github_repository_ruleset.conversation_resolution` — requires all review
  conversations to be resolved before merging.

## Usage

```bash
cd terraform
terraform init
terraform plan -var="github_token=<your-token>"
terraform apply -var="github_token=<your-token>"
```

## Linting

The Terraform configuration is linted with [tflint](https://github.com/terraform-linters/tflint)
using the bundled Terraform Language ruleset (`recommended` preset). The
configuration lives in `.tflint.hcl` in this directory.

```bash
cd terraform
tflint --init    # installs any declared plugins (bundled ruleset needs no install)
tflint -f compact
```

tflint is also run in CI via the `TFLint` workflow on every change to the
`terraform/` directory.

## Variables

| Name | Description | Default |
| ----------------- | ---------------------------------------------------- | ------------- |
| `github_token` | GitHub personal access token with `repo:admin` scope | _(required)_ |
| `github_owner` | GitHub repository owner | `tkoyama010` |
| `github_repository` | GitHub repository name | `pyvista-js` |
| `branch_name` | Branch to protect | `main` |
