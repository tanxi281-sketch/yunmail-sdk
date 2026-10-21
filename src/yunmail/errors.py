"""Exception types raised by the Yunmail SDK."""


class YunmailError(Exception):
    """Base class for all Yunmail SDK errors."""


class APIError(YunmailError):
    """The API returned a non-2xx response."""

    def __init__(self, status: int, message: str = "", payload=None):
        self.status = status
        self.payload = payload
        super().__init__(message or f"Yunmail API error (HTTP {status})")


class AuthenticationError(APIError):
    """HTTP 401/403 — the API key is missing, invalid or lacks scope."""


class RateLimitError(APIError):
    """HTTP 429 — too many requests; back off and retry."""
