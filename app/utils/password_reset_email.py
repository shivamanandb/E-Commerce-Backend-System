from .send_email import send_email
from ..exceptions import GeneralException
from fastapi import status


def send_password_reset_email(email: str, name: str, token: str) -> bool:
    """
    Sends a password reset email to the user.

    Args:
        email (str): Recipient's email address.
        name (str): User's full name.
        token (str): Reset token (valid for 5 minutes).

    Returns:
        bool: True if the email was sent successfully.

    Raises:
        GeneralException: If email sending fails.
    """
    try:
        subject = "Password Reset Request"

        # Your original HTML template
        html_template = """
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hello {{ name }},</p>
            <p>You requested to reset your password. Use the token below:</p>
            <p><strong>Reset Token: {{ token }}</strong></p>
            <p>This token will expire in 5 min.</p>
        </body>
        </html>
        """

        return send_email(
            email_to=email,
            subject=subject,
            html_template=html_template,
            environment={"name": name, "token": token}
        )

    except Exception as e:
        raise GeneralException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Failed to send password reset email: {str(e)}"
        )
