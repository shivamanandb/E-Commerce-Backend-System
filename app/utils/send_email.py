import emails
from emails.template import JinjaTemplate
from configuration.config import settings
import logging

logger = logging.getLogger(__name__)


def send_email(
    email_to: str,
    subject: str,
    html_template: str,
    environment: dict = {}
) -> bool:
    """
    Sends an HTML email using the `emails` library and SMTP.

    Args:
        email_to (str): Recipient's email address.
        subject (str): Email subject (can contain Jinja placeholders).
        html_template (str): HTML content of the email, using Jinja for variables.
        environment (dict): Key-value pairs for template rendering.

    Returns:
        bool: True if email sent successfully, False otherwise.

    Raises:
        Exception: Re-raises any SMTP/email-related errors after logging.
    """
    try:
        # Create email message with Jinja-templated subject and HTML content
        message = emails.html(
            html=JinjaTemplate(html_template),
            subject=JinjaTemplate(subject),
            mail_from=(settings.mail_from_name, settings.mail_from)
        )

        # Configure SMTP options
        smtp_options = {
            "host": settings.mail_server,
            "port": settings.mail_port,
            "user": settings.mail_username,
            "password": settings.mail_password,
            "tls": True
        }

        # Send the email
        response = message.send(to=email_to, render=environment, smtp=smtp_options)

        if response.status_code == 250:
            logger.info(f"Email sent successfully to {email_to}")
            return True
        else:
            logger.warning(f"Email sending failed with status {response.status_code} for {email_to}")
            return False

    except Exception as e:
        logger.error(f"Failed to send email to {email_to}: {str(e)}", exc_info=True)
        raise
