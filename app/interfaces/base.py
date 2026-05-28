"""Base model classes"""

from dataclasses import dataclass, field
from datetime import datetime


def _default_timestamp():
    """Return current timestamp"""
    return datetime.now().timestamp()


@dataclass
class BaseModel:
    """Base model with common fields"""

    created_at: float = field(default_factory=_default_timestamp, kw_only=True)
    updated_at: float = field(default_factory=_default_timestamp, kw_only=True)

    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now().timestamp()
