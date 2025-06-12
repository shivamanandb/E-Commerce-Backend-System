import uuid


def generate_reset_token() -> str:
    """
    Generates a cryptographically secure, unique token for password reset.

    Returns:
        str: A UUID-based reset token as a string.
    """
    return str(uuid.uuid4())
