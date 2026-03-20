# Fix for PR #251: check-pr-title Error

## Problem

PR #251 is failing the `check-pr-title` workflow because the title doesn't follow the Conventional Commits format.

**Current Title:** "Add uv lock check to pre-commit hooks"

**Error:**
```
No release type found in pull request title "Add uv lock check to pre-commit hooks".
Add a prefix to indicate what kind of release this pull request corresponds to.
```

## Root Cause

The repository uses the `amannn/action-semantic-pull-request` GitHub Action (defined in `.github/workflows/conventional-commits.yml`) to enforce Conventional Commits format on PR titles.

All PR titles must start with one of these prefixes:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `test:` - Test changes
- `build:` - Build system changes
- `ci:` - CI/CD configuration changes
- `chore:` - Other changes that don't modify src or test files
- `revert:` - Revert a previous commit

## Solution

Update the PR title from:
```
Add uv lock check to pre-commit hooks
```

To:
```
ci: add uv lock check to pre-commit hooks
```

### Why `ci:`?

The PR adds a pre-commit hook configuration (`.pre-commit-config.yaml`) which is part of the continuous integration/development workflow. This falls under the `ci:` category according to Conventional Commits conventions.

## How to Fix

### Option 1: Via GitHub Web UI
1. Go to https://github.com/tkoyama010/pyvista-js/pull/251
2. Click the "Edit" button next to the PR title
3. Change the title to: `ci: add uv lock check to pre-commit hooks`
4. Save the changes

### Option 2: Via GitHub CLI (gh)
```bash
gh pr edit 251 --title "ci: add uv lock check to pre-commit hooks"
```

### Option 3: Via API (requires appropriate permissions)
```bash
curl -X PATCH \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.github.com/repos/tkoyama010/pyvista-js/pulls/251 \
  -d '{"title":"ci: add uv lock check to pre-commit hooks"}'
```

## Verification

After updating the title, the `check-pr-title` workflow will automatically re-run and should pass. You can verify by checking:
- The workflow status in the PR's "Checks" tab
- The green checkmark appears next to "check-pr-title"

## Reference

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Repository's Conventional Commits Workflow](.github/workflows/conventional-commits.yml)
