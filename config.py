"""
Configuration module.

This module loads environment variables and exposes them via a dataclass
for centralized access across the application.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv


# Load environment variables from .env file (for local dev)
# In production, variables are usually set by the environment itself.
load_dotenv(override=True)


@dataclass(frozen=True)
class Config:
    """
    Application configuration values.

    Attributes:
        OPENAI_API_KEY (str): API key for OpenAI services.
        OPENAI_MODEL (str): Default model to use for agents.
        SENDGRID_API_KEY (str): API key for SendGrid email service.
        SENDER_EMAIL (str): Verified sender email address.
    """

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # SendGrid
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")

    # Email
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "")


# Create a global config instance
config = Config()
