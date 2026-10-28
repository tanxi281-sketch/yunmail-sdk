"""Yunmail Python SDK.

One unified client for Yunmail's cloud communications API:
transactional & marketing email, SMS, voice verification and push.
"""

from .client import YunmailClient
from .errors import (
    APIError,
    AuthenticationError,
    RateLimitError,
    YunmailError,
)
from .models import MessageResult

__version__ = "0.1.1"

__all__ = [
    "YunmailClient",
    "MessageResult",
    "YunmailError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "__version__",
]
