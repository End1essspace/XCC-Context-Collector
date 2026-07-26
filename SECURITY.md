# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| Current release | Yes |
| `main` during active development | Best effort |
| Older releases | No |

## Reporting a vulnerability

Use GitHub private vulnerability reporting:

https://github.com/End1essspace/xcc-context-collector/security/advisories/new

Do not open a public issue containing:

- credentials, API tokens, private keys, or connection strings;
- collected project source code or Git diffs;
- exploit details that would enable abuse;
- private filesystem paths or personal information.

Include the affected XCC version, Windows version, distribution type, reproduction steps, security impact, and the smallest sanitized proof of concept.

## Security model

XCC is local-first and does not upload collected context. Its sensitive-context detection is heuristic and is not a guarantee that every secret will be found. XCC warns before copying; it does not silently redact source code.

Official portable releases should include:

- a versioned ZIP;
- a matching `.sha256` file;
- a validated archive structure;
- `VERSION.txt` matching the executable release version.

Users should verify the SHA-256 checksum before running a downloaded archive.
