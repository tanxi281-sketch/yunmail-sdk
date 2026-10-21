import json
import unittest

from yunmail import (
    AuthenticationError,
    RateLimitError,
    YunmailClient,
)
from yunmail.client import YunmailClient as Client


class FakeTransport:
    """Records requests and replays queued (status, payload) responses."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def __call__(self, method, url, headers, body):
        self.requests.append((method, url, headers, body))
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


def make_client(responses):
    transport = FakeTransport(responses)
    client = Client(
        "test-key", transport=transport, sleeper=lambda _s: None
    )
    return client, transport


class SendEmailTest(unittest.TestCase):
    def test_send_email_posts_expected_payload(self):
        client, transport = make_client([(200, {"id": "m1", "status": "queued"})])
        result = client.send_email(
            "user@example.com", "Welcome", html="<p>Hi</p>", tags=["onboarding"]
        )
        self.assertEqual(result.id, "m1")
        self.assertEqual(result.channel, "email")
        method, url, headers, body = transport.requests[0]
        self.assertEqual(method, "POST")
        self.assertTrue(url.endswith("/email/send"))
        self.assertEqual(headers["Authorization"], "Bearer test-key")
        payload = json.loads(body.decode("utf-8"))
        self.assertEqual(payload["to"], "user@example.com")
        self.assertEqual(payload["tags"], ["onboarding"])

    def test_send_email_requires_content(self):
        client, _ = make_client([])
        with self.assertRaises(ValueError):
            client.send_email("user@example.com", "No body")


class SendSmsTest(unittest.TestCase):
    def test_send_sms_with_template(self):
        client, transport = make_client([(200, {"id": "s1", "status": "sent"})])
        result = client.send_sms(
            "+8613800000000", template_id="verify", params={"code": "123456"}
        )
        self.assertEqual(result.id, "s1")
        payload = json.loads(transport.requests[0][3].decode("utf-8"))
        self.assertEqual(payload["template_id"], "verify")
        self.assertEqual(payload["params"]["code"], "123456")


class ErrorMappingTest(unittest.TestCase):
    def test_401_raises_authentication_error(self):
        client, _ = make_client([(401, {"message": "invalid key"})])
        with self.assertRaises(AuthenticationError):
            client.get_message_status("m1")

    def test_429_retries_then_raises_rate_limit(self):
        client, transport = make_client([(429, {}), (429, {}), (429, {})])
        with self.assertRaises(RateLimitError):
            client.send_sms("+10000000000", content="hi")
        self.assertEqual(len(transport.requests), 3)  # 1 try + 2 retries

    def test_500_retries_then_succeeds(self):
        client, _ = make_client([(500, {}), (200, {"id": "v1", "status": "calling"})])
        result = client.send_voice_code("+10000000000", "123456")
        self.assertEqual(result.id, "v1")


class WebhookTest(unittest.TestCase):
    def test_verify_webhook(self):
        import hashlib
        import hmac

        payload = b'{"event":"delivered","id":"m1"}'
        secret = "whsec_test"
        signature = hmac.new(
            secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        self.assertTrue(YunmailClient.verify_webhook(payload, signature, secret))
        self.assertFalse(YunmailClient.verify_webhook(payload, "0" * 64, secret))


if __name__ == "__main__":
    unittest.main()
