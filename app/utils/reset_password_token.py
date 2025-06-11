from datetime import datetime, timezone
import uuid

def generate_reset_token():
    """
    Generate a unique reset password token.
    """
    token = str(uuid.uuid4())
    
    return token
