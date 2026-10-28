# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.1.1] - 2026-10-21

### Added
- `YunmailClient.from_env()` — build a client from the
  `YUNMAIL_API_KEY` / `YUNMAIL_BASE_URL` environment variables.
- `send_email_batch()` and `send_sms_batch()` convenience helpers that
  send the same message to many recipients, one send per recipient.
- `send_email()` now accepts `cc`, `bcc` and `reply_to`.

## [0.1.0] - 2026-10-21

### Added
- Initial public release of the Yunmail Python SDK.
- `YunmailClient` with `send_email`, `send_sms`, `send_voice_code`,
  `send_push` and `get_message_status`.
- Automatic retry with exponential backoff on HTTP 429 / 5xx.
- `YunmailClient.verify_webhook` for HMAC-SHA256 webhook signatures.
- Typed exceptions: `AuthenticationError`, `RateLimitError`, `APIError`.
