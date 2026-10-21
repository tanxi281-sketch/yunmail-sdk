"""Send an SMS verification code, with a voice-call fallback.

Usage:
    YUNMAIL_API_KEY=... python examples/send_sms_code.py
"""

import os

from yunmail import APIError, YunmailClient

client = YunmailClient(api_key=os.environ["YUNMAIL_API_KEY"])

phone = "+8613800000000"
code = "123456"

try:
    result = client.send_sms(to=phone, template_id="verify_code", params={"code": code})
    print("sms sent:", result.id)
except APIError:
    # Fall back to a voice call when SMS cannot reach the handset.
    result = client.send_voice_code(to=phone, code=code)
    print("voice fallback:", result.id)
