from fastapi import Depends
from .middlewares.oauth2 import get_current_user
from .exceptions import AuthException
from .auth.models import User


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that ensures the current user has admin privileges.

    Args:
        current_user (User): Authenticated user injected by dependency.

    Returns:
        User: The same user if authorized.

    Raises:
        AuthException: If the user is not an admin.
    """
    if current_user.role.value != "admin":
        raise AuthException("Access denied: Admins only.")
    return current_user


async def require_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that ensures the current user is a regular user.

    Args:
        current_user (User): Authenticated user injected by dependency.

    Returns:
        User: The same user if authorized.

    Raises:
        AuthException: If the user is not a regular user.
    """
    if current_user.role.value != "user":
        raise AuthException("Access denied: Users only.")
    return current_user
