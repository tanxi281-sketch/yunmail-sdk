# Yunmail Python SDK

Official Python SDK for the [Yunmail](https://www.yunmail.cc.cd) cloud
communications platform — **email, SMS, voice verification and push
notifications through one unified API**, with a single API key.

- 📧 Transactional & marketing email with template support
- 💬 SMS verification codes, alerts and campaigns (200+ countries/regions)
- 📞 Voice OTP as a reliable fallback where SMS can't reach
- 🔔 App & web push notifications
- 🔐 HMAC-SHA256 webhook signature verification built in
- 🚀 Zero dependencies — Python standard library only

> Status: **0.1.1 (alpha)**. The API surface covers the four core send
> channels plus delivery-status lookup. See [ROADMAP.md](ROADMAP.md).

## Installation

```bash
pip install yunmail
```

Or from source:

```bash
git clone https://github.com/tanxi281-sketch/yunmail-sdk.git
cd yunmail-sdk
pip install -e .
```

## Quickstart

```python
from yunmail import YunmailClient

client = YunmailClient(api_key="YOUR_YUNMAIL_API_KEY")

# Email
client.send_email(
    to="user@example.com",
    subject="Welcome to Yunmail",
    html="<p>Thanks for signing up!</p>",
)

# SMS verification code (template based)
client.send_sms(
    to="+8613800000000",
    template_id="verify_code",
    params={"code": "123456"},
)

# Voice OTP fallback
client.send_voice_code(to="+8613800000000", code="123456")

# Push notification
client.send_push(
    device_tokens=["device-token-1"],
    title="Order shipped",
    body="Your order is on its way.",
)

# Delivery status of any message
status = client.get_message_status("MESSAGE_ID")
```

## Webhook verification

Verify that a webhook really came from Yunmail before trusting it:

```python
from yunmail import YunmailClient

ok = YunmailClient.verify_webhook(
    payload=request_body_bytes,        # raw request body
    signature=request.headers["X-Yunmail-Signature"],
    secret="YOUR_WEBHOOK_SECRET",
)
```

## Error handling

```python
from yunmail import AuthenticationError, RateLimitError, APIError

try:
    client.send_email(...)
except AuthenticationError:
    ...  # bad or under-scoped API key (HTTP 401/403)
except RateLimitError:
    ...  # HTTP 429 — the client already retried with backoff
except APIError as exc:
    print(exc.status, exc.payload)
```

HTTP 429 and 5xx responses are retried automatically with exponential
backoff (`max_retries=2` by default).

## Development

```bash
python -m unittest discover -s tests -v
```

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache License 2.0 — see [LICENSE](LICENSE).
