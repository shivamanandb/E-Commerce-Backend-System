from datetime import datetime, timedelta
from jose import JWTError, jwt 


def reset_password_token(email: str):
    data = {"sub": email, "exp": datetime.now() + timedelta(minutes=5)}
    token = jwt.encode(data, FORGET_PASSWORD_SECRET_KEY, )