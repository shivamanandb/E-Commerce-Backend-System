import emails
from emails.template import JinjaTemplate 
from ..configuration.config import settings
import logging

logger = logging.getLogger(__name__)

def send_email(
    email_to: str,
    subject: str,
    html_template: str,
    environment: dict = {}
) -> bool:
    """Send email using emails library"""
    try:
        message = emails.html(
            html=JinjaTemplate(html_template),
            subject=JinjaTemplate(subject),
            mail_from=(settings.mail_from_name, settings.mail_from)
        )
        
        smtp_options = {
            "host": settings.mail_server,
            "port": settings.mail_port,
            "user": settings.mail_username,
            "password": settings.mail_password,
            "tls": True
        }

        
        response = message.send(to=email_to, render=environment, smtp=smtp_options)
        logger.info(f"Email sent to {email_to}: {response.status_code}")
        return response.status_code
        
    except Exception as e:
        logger.error(f"Failed to send email to {email_to}: {str(e)}")
        return False