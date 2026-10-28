# Roadmap

## 0.1.0 (initial public release)
- [x] Unified client for email, SMS, voice verification and push
- [x] Automatic retry with backoff on HTTP 429 / 5xx
- [x] Webhook HMAC-SHA256 signature verification
- [x] Unit tests with an injectable transport (no network needed)

## 0.1.1
- [x] Published to PyPI (`pip install yunmail`)
- [x] Batch sending helpers for email and SMS
- [x] `YunmailClient.from_env()` and email cc/bcc/reply_to support

## Next
- [ ] Async client (`asyncio`) alongside the sync client
- [ ] Template management endpoints (list / create / delete)
- [ ] Delivery analytics queries (rates, failure attribution)
- [ ] Node.js SDK in a sibling repository

## Longer term
- [ ] Go and PHP SDKs
- [ ] CLI tool for sending test messages and checking status
