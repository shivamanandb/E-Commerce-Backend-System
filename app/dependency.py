from fastapi import Depends
from .middlewares.oauth2 import get_current_user
from .exceptions import AuthException
from .auth.models import User

async def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise AuthException("Only admins are allowed to access this resource")
    return current_user

async def require_user(current_user: User = Depends(get_current_user)):
    if current_user.role.value != "user":
        raise AuthException("Only normal user are allowed to access this resource")
    return current_user
