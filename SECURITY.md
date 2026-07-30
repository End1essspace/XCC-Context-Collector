# Security Policy

## Supported versions

| Version | Security support |
|---|---|
| Current stable release | Supported |
| `main` during active development | Best effort |
| Superseded releases | Not supported |

Users should update to the latest published release before reporting a defect that may already be fixed.

## Reporting a vulnerability

Use GitHub private vulnerability reporting:

https://github.com/End1essspace/xcc-context-collector/security/advisories/new

Do not open a public issue containing:

- credentials, API tokens, private keys, or connection strings;
- collected project source or Git diffs;
- exploit details that enable abuse;
- proprietary repository information;
- private filesystem paths, usernames, or personal data.

Include:

```text
Affected XCC version:
Distribution: packaged ZIP or source checkout
Windows version and architecture:
Affected workflow or component:
Reproduction steps:
Security impact:
Smallest sanitized proof of concept:
```

## Security model

XCC is a local-first utility:

- it does not require an account;
- it does not include cloud upload or telemetry;
- generated context is copied to the local Windows clipboard;
- settings are stored under `%USERPROFILE%\.xcc\config.json`;
- runtime history is in-memory and stores metadata only.

The application may read files explicitly selected by the user or discovered under a selected project root. Users remain responsible for reviewing the selected source and the final clipboard content before sharing it with an external AI service.

## Sensitive-context detection

XCC performs heuristic detection for sensitive filenames, private-key headers, likely tokens, credential assignments, and credential-bearing connection strings.

Important limits:

- detection can produce false positives;
- detection can miss secrets;
- XCC does not silently redact or modify source code;
- disabling **Safety confirmation** disables only the modal prompt, not detection or warning metadata;
- warning summaries do not display detected values.

This feature is a visibility aid, not a secret-scanning guarantee.

## Release integrity

Official portable releases should include:

```text
XCC-Context-Collector-v<version>-win64.zip
XCC-Context-Collector-v<version>-win64.zip.sha256
```

The release process validates:

- safe ZIP paths;
- one application root directory;
- required executable and runtime files;
- `VERSION.txt` matching the canonical version;
- the companion SHA-256 checksum;
- clean-host Windows 10 and Windows 11 evidence for the same archive hash.

Users should verify the checksum before running a downloaded archive. v1.2.0 binaries are not code-signed; checksum verification and downloading only from the official repository are therefore especially important.

## Clipboard and local-data considerations

After a successful collection, the generated context remains in the Windows clipboard until another application replaces it. Clear or replace the clipboard after sharing sensitive project context.

Deleting the extracted portable folder does not remove saved settings. Remove `%USERPROFILE%\.xcc` separately when local configuration should also be deleted.
