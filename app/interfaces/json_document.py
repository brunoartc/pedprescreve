"""JSON document model"""

from dataclasses import dataclass
from typing import Any
import uuid

from .base import BaseModel


@dataclass
class JsonDocument(BaseModel):
    """Generic JSON document persisted in DynamoDB"""

    title: str
    payload: dict[str, Any]
    id: str | None = None

    def __post_init__(self):
        """Ensure ID is always a valid UUID string."""

        if not self.id or not str(self.id).strip():
            self.id = str(uuid.uuid4())
            return

        self.id = str(uuid.UUID(str(self.id)))
