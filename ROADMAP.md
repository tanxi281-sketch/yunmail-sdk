# Roadmap

## 0.1.0 (initial public release)
- [x] Unified client for email, SMS, voice verification and push
- [x] Automatic retry with backoff on HTTP 429 / 5xx
- [x] Webhook HMAC-SHA256 signature verification
- [x] Unit tests with an injectable transport (no network needed)

## Next
- [ ] Publish to PyPI (`pip install yunmail`)
- [ ] Async client (`asyncio`) alongside the sync client
- [ ] Template management endpoints (list / create / delete)
- [ ] Batch sending helpers for email and SMS
- [ ] Delivery analytics queries (rates, failure attribution)
- [ ] Node.js SDK in a sibling repository

## Longer term
- [ ] Go and PHP SDKs
- [ ] CLI tool for sending test messages and checking status
