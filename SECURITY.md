# Security Policy

## Reporting a vulnerability

Please do not open a public issue for a suspected vulnerability. Contact the repository owner privately with a description, reproduction steps, and potential impact.

## Log-data safety

OpsPulse runs locally and makes no network requests. Its reports mask common identifiers and IP addresses in normalized error signatures, but source messages may still contain secrets or personal data. Use sanitized samples in public repositories and review generated reports before sharing.

