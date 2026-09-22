# XCC Runtime History Format — M17.7

XCC persists operational history locally at:

```text
%USERPROFILE%\.xcc\history.json
```

The same schema is used by **History → Export JSON**.

## Envelope

```json
{
  "schema_version": 1,
  "format": "xcc-runtime-history",
  "privacy": "metadata-only",
  "records": []
}
```

Records are newest-first and persistence is bounded to the newest 200 records.

## Collection record

`type` is `collection`. Stored fields are operational metadata only: timestamp, mode name, sanitized source label, outcome, duration, counts/character totals, truncation state, and warning/error counts. Absolute private filesystem source paths are converted to non-path labels such as `Project folder` or `Git repository`.

## Attachment record

`type` is `attachment`. Stored fields are timestamp, transfer type/outcome, file count, aggregate bytes, duration, filename-warning count, and optionally the generated ZIP filename. Absolute attachment paths are never stored.

## Explicitly excluded

History persistence/export does **not** contain:

- collected source bodies;
- Git diff bodies;
- detected secret values;
- raw failure/exception bodies;
- attachment file contents;
- attachment source paths;
- absolute private collection source paths by default.

## Corruption recovery

Unreadable or unsupported top-level documents are moved beside the store as `history.corrupt-YYYYMMDD-HHMMSS.json`; XCC then starts with a clean store. If only individual records are malformed, valid records are retained and malformed records are skipped.

## Retention

The store keeps the newest 200 records. `Clear History` deletes persisted event metadata by replacing the store with an empty valid document; it does not delete source files, attachment files, or generated ZIP bundles.
