# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] - 2026-10-21

### Added
- Initial public release of the Yunmail Python SDK.
- `YunmailClient` with `send_email`, `send_sms`, `send_voice_code`,
  `send_push` and `get_message_status`.
- Automatic retry with exponential backoff on HTTP 429 / 5xx.
- `YunmailClient.verify_webhook` for HMAC-SHA256 webhook signatures.
- Typed exceptions: `AuthenticationError`, `RateLimitError`, `APIError`.
