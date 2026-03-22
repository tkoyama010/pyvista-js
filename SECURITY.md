<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Security Policy](#security-policy)
  - [Supported Versions](#supported-versions)
  - [SPEC 8 — Securing the Release Process](#spec-8--securing-the-release-process)
  - [Reporting a Vulnerability](#reporting-a-vulnerability)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Security Policy

[![SPEC 8 — Securing the Release Process](https://img.shields.io/badge/SPEC-8-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0008/)

## Supported Versions

| Version | Supported |
| ------- | ------------------ |
| latest | :white_check_mark: |

## SPEC 8 — Securing the Release Process

This project follows [SPEC 8](https://scientific-python.org/specs/spec-0008/) for securing the release process:

- **Trusted Publishing**: Releases are published to PyPI using OpenID Connect (OIDC) trusted publishing, eliminating the need for long-lived API tokens
- **Build Provenance Attestations**: All PyPI releases include cryptographically signed build provenance attestations generated using Sigstore
- **Pinned Actions**: All GitHub Actions are pinned to specific commit SHAs to prevent supply chain attacks
- **Secure Build Environment**: Builds run in ephemeral GitHub Actions runners with minimal permissions

You can verify the attestations for any release by downloading the artifacts from PyPI and using the [PyPI attestation verification tools](https://docs.pypi.org/attestations/).

## Reporting a Vulnerability

If you discover a security vulnerability in pyvista-js, please report it responsibly.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via [GitHub's private vulnerability reporting](https://github.com/tkoyama010/pyvista-js/security/advisories/new).

Include as much of the following information as possible:

- Type of issue (e.g., code injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the issue
- Steps to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue

We will acknowledge receipt of your report and work with you to understand and address the issue.
