"""
Email agent module.

Defines the SendGrid-powered email sending tool and wraps it in an Agent
that formats research reports into HTML emails.
"""

import logging
from typing import Dict

import sendgrid
from sendgrid.helpers.mail import Content, Email, Mail, To

from agents import Agent, function_tool
from deep_research.config import Config

logger = logging.getLogger(__name__)


@function_tool
def send_email(receiver_email: str, subject: str, html_body: str) -> Dict[str, str]:
    """
    Send an email using SendGrid.

    Args:
        receiver_email (str): The recipient email address.
        subject (str): The subject line of the email.
        html_body (str): The email body, in HTML format.

    Returns:
        dict: A dictionary with the status of the operation.
    """
    sg = sendgrid.SendGridAPIClient(api_key=Config.SENDGRID_API_KEY)

    from_email = Email(Config.SENDER_EMAIL)  # verified sender
    to_email = To(receiver_email)
    content = Content("text/html", html_body)

    mail = Mail(from_email, to_email, subject, content).get()
    response = sg.client.mail.send.post(request_body=mail)

    logger.info("Email response status: %s", response.status_code)
    return {"status": "success"}


INSTRUCTIONS = """You will be given:
1. A receiver email address
2. A subject line
3. A markdown report

Your job:
- Convert the markdown report into clean, well-presented HTML.
- Call the `send_email` tool with (receiver_email, subject, html_body).
- Send exactly one email, and do not output anything else.
"""


email_agent = Agent(
    name="EmailAgent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model=Config.OPENAI_MODEL,
)
