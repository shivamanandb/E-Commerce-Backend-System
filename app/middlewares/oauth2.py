from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer 
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError

from ..configuration.config import settings
from ..configuration.database import get_db
from ..exceptions import InvalidCredentialsException, UserNotFoundException
from ..auth import models
from . import schema

# FastAPI dependency to extract token from Authorization header
# It expects "Authorization: Bearer <token>" format
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/signin')

# Security Configurations
ACCESS_TOKEN_SECRET_KEY = settings.access_token_secret_key
REFRESH_TOKEN_SECRET_KEY = settings.refresh_token_secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days


# -------------------------
# Generate JWT Access Token
# -------------------------
def create_access_token(data: dict) -> str:
    """
    Creates a short-lived JWT access token used for authenticating requests.

    Args:
        data (dict): Payload to encode in the token (e.g., user_id, role).

    Returns:
        str: Encoded JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, ACCESS_TOKEN_SECRET_KEY, algorithm=ALGORITHM)


# --------------------------
# Generate JWT Refresh Token
# --------------------------
def create_refresh_token(data: dict) -> str:
    """
    Creates a long-lived JWT refresh token used to issue new access tokens.

    Args:
        data (dict): Payload to encode in the token (e.g., user_id, role).

    Returns:
        str: Encoded JWT refresh token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, REFRESH_TOKEN_SECRET_KEY, algorithm=ALGORITHM)


# ----------------------
# Verify JWT Access Token
# ----------------------
def verify_access_token(token: str, credentials_exception) -> schema.TokenData:
    """
    Verifies a JWT token's validity and decodes it to extract user details.

    Args:
        token (str): JWT token from client.
        credentials_exception: Exception to raise on failure.

    Returns:
        schema.TokenData: Decoded payload with user_id and role.
    """
    try:
        payload = jwt.decode(token, ACCESS_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")

        if user_id is None or role is None:
            raise credentials_exception

        return schema.TokenData(id=int(user_id), role=role)
    
    except JWTError:
        raise credentials_exception


# ---------------------
# Get Authenticated User
# ---------------------
async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> models.User:
    """
    Fetches the current logged-in user from the database using the JWT token.

    Args:
        token (str): Auto-injected from Authorization header.
        db (AsyncSession): DB session dependency.

    Returns:
        models.User: Authenticated user object from the DB.
    """
    credentials_exception = InvalidCredentialsException("Could not validate credentials")
    
    token_data = verify_access_token(token, credentials_exception)

    result = await db.execute(select(models.User).where(models.User.id == token_data.id))
    user = result.scalar_one_or_none()

    if user is None:
        raise UserNotFoundException(f"User not found for this id: {token_data.id}")

    return user
