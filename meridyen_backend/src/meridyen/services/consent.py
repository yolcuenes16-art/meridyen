from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from meridyen.domain.models import ConsentRecord, Mode


class ConsentService:
    """In-memory implementation with explicit purpose limitation; swap storage via this boundary."""
    def __init__(self): self._records: dict[UUID, ConsentRecord] = {}

    def set_mode_consent(self, user_id: UUID, mode: Mode, consent: bool) -> ConsentRecord | None:
        if not consent:
            self._records.pop(user_id, None)
            return None
        record = ConsentRecord(user_id=user_id, mode=mode, consented_at=datetime.now(timezone.utc))
        self._records[user_id] = record
        return record

    def mode_for(self, user_id: UUID) -> Mode | None:
        record = self._records.get(user_id)
        return record.mode if record else None
