"""Yunmail API client.

Covers the four Yunmail channels — email, SMS, voice verification and
push notifications — through one REST client with a single API key.

The transport is injectable, which keeps the SDK dependency-free
(standard library only) and easy to test: pass any callable with the
signature ``transport(method, url, headers, body) -> (status, headers,
body)``.
"""

import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, Iterable, Optional, Sequence, Tuple

from .errors import APIError, AuthenticationError, RateLimitError
from .models import MessageResult

DEFAULT_BASE_URL = "https://api.yunmail.cc.cd/v1"

Transport = Callable[
    [str, str, Dict[str, str], Optional[bytes]],
    Tuple[int, Dict[str, str], bytes],
]


def _urllib_transport(method, url, headers, body):
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as exc:  # non-2xx still carries a body
        return exc.code, dict(exc.headers or {}), exc.read()
    except urllib.error.URLError as exc:
        raise APIError(0, f"Network error calling Yunmail API: {exc.reason}") from exc


class YunmailClient:
    """Client for the Yunmail cloud communications API.

    Args:
        api_key: Your Yunmail API key (sent as a Bearer token).
        base_url: API base URL; override for staging or self-hosted use.
        timeout: Per-request timeout in seconds (default transport only).
        max_retries: Retries on HTTP 429 / 5xx with exponential backoff.
        transport: Custom transport callable (mainly for testing).
        sleeper: Sleep function used between retries (mainly for testing).
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 30,
        max_retries: int = 2,
        transport: Optional[Transport] = None,
        sleeper: Callable[[float], None] = time.sleep,
    ):
        if not api_key:
            raise ValueError("api_key is required")
        self.api_key = api_key

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._transport = transport or _urllib_transport
        self._sleeper = sleeper

    @classmethod
    def from_env(cls, **kwargs) -> "YunmailClient":
        """Create a client from environment variables.

        Reads ``YUNMAIL_API_KEY`` (required) and ``YUNMAIL_BASE_URL``
        (optional). Extra keyword arguments are passed to the constructor.
        """
        api_key = os.environ.get("YUNMAIL_API_KEY")
        if not api_key:
            raise ValueError("YUNMAIL_API_KEY environment variable is not set")
        kwargs.setdefault("api_key", api_key)
        base_url = os.environ.get("YUNMAIL_BASE_URL")
        if base_url:
            kwargs.setdefault("base_url", base_url)
        return cls(**kwargs)

    # ------------------------------------------------------------------
    # Channels
    # ------------------------------------------------------------------
    def send_email(
        self,
        to: str,
        subject: str,
        html: Optional[str] = None,
        text: Optional[str] = None,
        from_addr: Optional[str] = None,
        cc: Optional[Sequence[str]] = None,
        bcc: Optional[Sequence[str]] = None,
        reply_to: Optional[str] = None,
        tags: Optional[Sequence[str]] = None,
    ) -> MessageResult:
        """Send a transactional or marketing email."""
        if html is None and text is None:
            raise ValueError("either html or text content is required")
        payload: Dict[str, Any] = {"to": to, "subject": subject}
        if html is not None:
            payload["html"] = html
        if text is not None:
            payload["text"] = text
        if from_addr is not None:
            payload["from"] = from_addr
        if cc:
            payload["cc"] = list(cc)
        if bcc:
            payload["bcc"] = list(bcc)
        if reply_to is not None:
            payload["reply_to"] = reply_to
        if tags:
            payload["tags"] = list(tags)
        return self._send("/email/send", payload, channel="email")

    def send_email_batch(
        self, recipients: Iterable[str], **kwargs
    ) -> "list[MessageResult]":
        """Send the same email to many recipients, one send per recipient.

        Convenience wrapper around :meth:`send_email`; keyword arguments
        (subject, html/text, from_addr, cc, bcc, reply_to, tags) are shared
        by every send. Returns one result per recipient, in order.
        """
        return [self.send_email(to=r, **kwargs) for r in recipients]

    def send_sms_batch(
        self, recipients: Iterable[str], **kwargs
    ) -> "list[MessageResult]":
        """Send the same SMS to many recipients, one send per recipient.

        Convenience wrapper around :meth:`send_sms`; keyword arguments
        (content or template_id/params) are shared by every send.
        """
        return [self.send_sms(to=r, **kwargs) for r in recipients]

    def send_sms(
        self,
        to: str,
        content: Optional[str] = None,
        template_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> MessageResult:
        """Send an SMS (verification code, alert or marketing message)."""
        if content is None and template_id is None:
            raise ValueError("either content or template_id is required")
        payload: Dict[str, Any] = {"to": to}
        if content is not None:
            payload["content"] = content
        if template_id is not None:
            payload["template_id"] = template_id
        if params:
            payload["params"] = params
        return self._send("/sms/send", payload, channel="sms")

    def send_voice_code(
        self,
        to: str,
        code: str,
        lang: str = "en-US",
    ) -> MessageResult:
        """Deliver a one-time passcode by voice call (SMS fallback)."""
        payload = {"to": to, "code": code, "lang": lang}
        return self._send("/voice/send", payload, channel="voice")

    def send_push(
        self,
        device_tokens: Iterable[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> MessageResult:
        """Send an app/web push notification to one or more devices."""
        payload: Dict[str, Any] = {
            "device_tokens": list(device_tokens),
            "title": title,
            "body": body,
        }
        if data:
            payload["data"] = data
        return self._send("/push/send", payload, channel="push")

    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """Fetch the delivery status of a previously sent message."""
        return self._request("GET", f"/messages/{message_id}")

    # ------------------------------------------------------------------
    # Webhooks
    # ------------------------------------------------------------------
    @staticmethod
    def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
        """Verify an HMAC-SHA256 webhook signature in constant time."""
        expected = hmac.new(
            secret.encode("utf-8"), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature.strip())

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _send(self, path: str, payload: Dict[str, Any], channel: str) -> MessageResult:
        data = self._request("POST", path, payload)
        return MessageResult.from_payload(data, channel=channel)

    def _request(
        self, method: str, path: str, payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "yunmail-python/0.1.1",
        }
        body = json.dumps(payload).encode("utf-8") if payload is not None else None

        attempt = 0
        while True:
            status, _resp_headers, raw = self._transport(method, url, headers, body)
            if 200 <= status < 300:
                return json.loads(raw.decode("utf-8")) if raw else {}
            retryable = status == 429 or status >= 500
            if retryable and attempt < self.max_retries:
                self._sleeper(0.5 * (2**attempt))
                attempt += 1
                continue
            self._raise_for_status(status, raw)

    @staticmethod
    def _raise_for_status(status: int, raw: bytes):
        payload = None
        message = ""
        if raw:
            try:
                payload = json.loads(raw.decode("utf-8"))
                message = payload.get("message") or payload.get("error") or ""
            except (ValueError, UnicodeDecodeError):
                message = raw.decode("utf-8", errors="replace")[:200]
        if status in (401, 403):
            raise AuthenticationError(status, message, payload)
        if status == 429:
            raise RateLimitError(status, message, payload)
        raise APIError(status, message, payload)
