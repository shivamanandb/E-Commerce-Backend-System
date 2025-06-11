
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

@router.post("/refresh", response_model=schema.Token)
async def refresh_token(refresh_token: str = Form(...), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=settings.algorithm)
        user_id = payload.get("user_id")

        # Optional: validate if token exists in DB

        new_access_token = create_access_token({"user_id": user_id, "role": payload["role"]})
        new_refresh_token = create_refresh_token(payload)
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise InvalidTokenException("Invalid refresh token")
