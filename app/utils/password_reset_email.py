from .send_email import send_email

def send_password_reset_email(email: str, name: str, token: str) -> bool:
    """Send password reset email"""
    subject = "Password Reset Request"
    
    html_template = """
    <html>
    <body>
        <h2>Password Reset Request</h2>
        <p>Hello {{ name }},</p>
        <p>You requested to reset your password. Use the token below:</p>
        <p><strong>Reset Token: {{ token }}</strong></p>
        <p>This token will expire in 1 hour.</p>
        <p>If you didn't request this, please ignore this email.</p>
    </body>
    </html>
    """
    
    return send_email(
        email_to=email,
        subject=subject,
        html_template=html_template,
        environment={"name": name, "token": token}
    )