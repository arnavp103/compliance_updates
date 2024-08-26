"""
This script emails relevant stakeholders with relevant updates.
"""

from datetime import datetime
import logging
from postmarker.core import PostmarkClient
from dotenv import dotenv_values


def email_updates(updates: list[dict[str, str]], stakeholders: list[str]):
    """Email the stakeholders with the new updates."""

    # postmark api key
    config = dotenv_values(".env")
    postmark_api_key = config["POSTMARK_API_KEY"]
    if postmark_api_key is None:
        logging.error("No Postmark API key found")

    pm = PostmarkClient(server_token=postmark_api_key)
    subject = (
        f"UAE Central Bank Rulebook Updates - {datetime.now().strftime('%d %B %Y')}"
    )

    logging.debug("Sending emails to %s", stakeholders)
