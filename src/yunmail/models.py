"""Response models returned by the Yunmail SDK."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class MessageResult:
    """Result of a send request (email / SMS / voice / push)."""

    id: Optional[str] = None
    status: Optional[str] = None
    channel: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: Dict[str, Any], channel: str) -> "MessageResult":
        return cls(
            id=payload.get("id") or payload.get("message_id"),
            status=payload.get("status"),
            channel=channel,
            raw=payload,
        )
