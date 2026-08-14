# Security Policy

## Reporting a Vulnerability

We take the security of the Vymed backend service seriously. If you discover a security vulnerability:

1. **Do not** disclose it publicly, and **do not** submit it as a normal GitHub issue.
2. Report it privately via GitHub's **Security → Report a vulnerability** (private vulnerability reporting) on this repository.
3. Include a description of the issue, the affected endpoint or service, and steps to reproduce if possible.

## What to Expect

- Acknowledgment of your report within 48 hours.
- Regular updates on triage and fix progress.
- Credit for the discovery if you wish.

## Data Note

This service may handle health/supply-chain related data. Never commit real credentials or production data to this repository; use the `.env` mechanism and keep secrets out of git.

## Supported Versions

| Version | Supported |
|---|---|
| 0.1.x | ✅ |

## Note

This project is under active development. Treat it as pre-release software until the security posture has been reviewed.
