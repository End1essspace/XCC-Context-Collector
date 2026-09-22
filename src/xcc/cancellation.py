from __future__ import annotations


class CollectionCancelled(RuntimeError):
    """Raised when a collection job is cooperatively cancelled."""


class AttachmentBundleCancelled(RuntimeError):
    """Raised when attachment bundle creation is cooperatively cancelled."""
