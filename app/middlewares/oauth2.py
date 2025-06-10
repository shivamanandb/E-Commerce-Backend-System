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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login') # is creating a dependency for extracting a bearer token from the Authorization header in FastAPI — specifically for OAuth2 password flow.

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

        print("payload: ", payload)

        user_id: str = payload.get("user_id")
        role: str = payload.get("role")  

        print("user_id:", user_id, "role:", role)

        if user_id is None or role is None:
            raise credentials_exception

        token_data = schema.TokenData(id=int(user_id), role=role) 

    except JWTError:
        raise credentials_exception

    return token_data

    
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    
    """
    Purpose: Get the logged-in user object from the database using the token.
    token: Automatically extracted from Authorization: Bearer <token> header by oauth2_scheme.
    db: Injects the DB session using FastAPI’s dependency injection.
    """
    credentials_exception = InvalidCredentialsException("could not validate credentails")
    
    token =  verify_access_token(token, credentials_exception)
    print("token: ", token)
    
    user = await db.execute(select(models.User).where(models.User.id == token.id))
    user = user.scalar_one_or_none()
    if user is None:
        raise UserNotFoundException(f"User not found for this id: {token.id}")
    
    return user
