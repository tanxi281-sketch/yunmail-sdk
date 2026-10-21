"""Send a transactional email with the Yunmail Python SDK.

Usage:
    YUNMAIL_API_KEY=... python examples/send_email.py
"""

import os

from yunmail import YunmailClient

client = YunmailClient(api_key=os.environ["YUNMAIL_API_KEY"])

result = client.send_email(
    to="user@example.com",
    subject="Welcome to Yunmail",
    html="<p>Thanks for signing up!</p>",
    text="Thanks for signing up!",
    tags=["onboarding"],
)
print("queued:", result.id, result.status)
