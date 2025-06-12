from fastapi import APIRouter, Depends, Form
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ..configuration import logger_config
from . import schema
from ..configuration.database import get_db
from ..configuration.config import settings
from .oauth2 import create_access_token, create_refresh_token
from ..exceptions import InvalidTokenException

router = APIRouter()
logger = logging.getLogger(__name__)


# -----------------------------
# Refresh JWT Access & Refresh
# -----------------------------
@router.post("/refresh", response_model=schema.Token)
async def refresh_token(
    refresh_token: str = Form(...), 
    db: AsyncSession = Depends(get_db)
):
    """
    Refreshes an expired access token using a valid refresh token.

    Args:
        refresh_token (str): The refresh token sent from the client.
        db (AsyncSession): Optional DB session if you plan to validate refresh tokens from DB.

    Returns:
        schema.Token: A new access and refresh token pair.
    
    Raises:
        InvalidTokenException: If the refresh token is invalid or tampered.
    """
    try:
        # Decode and validate the refresh token
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Extract user information from token payload
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")

        if user_id is None or role is None:
            raise InvalidTokenException("Missing user_id or role in refresh token")

        # Log token refresh event (optional)
        logger.info(f"Issuing new access token for user_id: {user_id}")

        # Generate new tokens
        new_access_token = create_access_token({"user_id": user_id, "role": role})
        new_refresh_token = create_refresh_token({"user_id": user_id, "role": role})

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    except JWTError as e:
        logger.warning(f"Refresh token validation failed: {str(e)}")
        raise InvalidTokenException("Invalid refresh token")
