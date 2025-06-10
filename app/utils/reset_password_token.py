from datetime import datetime, timedelta
from jose import JWTError, jwt 
from ..configuration.config import settings

FORGET_PASSWORD_SECRET_KEY = settings.forget_password_secret_key
ALGORITHM = settings.algorithm

def reset_password_token(email: str):
    data = {"sub": email}
    token = jwt.encode(data, FORGET_PASSWORD_SECRET_KEY, ALGORITHM)
    return token