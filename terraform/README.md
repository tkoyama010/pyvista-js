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

## CI Plan & Apply

In addition to TFLint, the `Terraform` GitHub Actions workflow
(`.github/workflows/terraform.yml`) automates `terraform plan` and
`terraform apply` using [tfcmt](https://github.com/suzuki-shunsuke/tfcmt)
so that plan output is posted directly as a PR comment for review.

### Workflow jobs

| Job | Trigger | Action |
| ------ | -------------------------------- | ----------------------------------------------------- |
| `plan` | `pull_request` targeting `main` | Runs `terraform plan` and posts the result as a PR comment. |
| `apply`| `push` to `main` | Runs `terraform apply -auto-approve` and posts the result. |

Both jobs only run when files under `terraform/` or the workflow file itself
change.

### Required secret

The workflow passes the `github_token` Terraform variable from the
`TF_GITHUB_TOKEN` repository secret. Create a GitHub personal access token
(or fine-grained token) with `repo:admin` scope and add it as a repository
secret named `TF_GITHUB_TOKEN`.

> **Note:** tfcmt uses the auto-generated `GITHUB_TOKEN` (with
> `pull-requests: write` permission) to post comments, so no extra token is
> needed for commenting.

## Variables

| Name | Description | Default |
| ----------------- | ---------------------------------------------------- | ------------- |
| `github_token` | GitHub personal access token with `repo:admin` scope | _(required)_ |
| `github_owner` | GitHub repository owner | `tkoyama010` |
| `github_repository` | GitHub repository name | `pyvista-js` |
