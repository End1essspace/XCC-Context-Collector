from __future__ import annotations


class CollectionCancelled(RuntimeError):
    """Raised when a collection job is cooperatively cancelled."""
