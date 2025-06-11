from fastapi import APIRouter, status, Depends, BackgroundTasks
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta, timezone
from ..middlewares import oauth2
from . import schemas, models
from ..auth.models import ResetPasswordToken
from ..configuration.config import settings 
import logging
from ..configuration import logger_config
from ..exceptions import EmailAlreadyExistsException, UserNotFoundException, InvalidPasswordException, InvalidTokenException
from sqlalchemy.exc import IntegrityError
from ..configuration.database import get_db
from .schemas import ForgotPasswordRequest
from ..utils import password_encoder
from . import models
from ..utils import password_encoder 
from ..utils.reset_password_token import generate_reset_token
from ..utils.password_reset_email import send_password_reset_email
from ..auth.schemas import ResetPasswordRequest
from ..auth.models import ResetPasswordToken

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(user: schemas.CreateUser, db: AsyncSession = Depends(get_db)) -> schemas.UserResponse:
    """
    Create a user after validating details and then hashing password
    """
    
    # All required details must be filled
    # check email is valid or not
    # Hash Password
    # Save data into db 
    
    try:
        hashed_password = password_encoder.hash(user.password)
        user.password = hashed_password
        
        # unpack dictionary
        new_user = models.User(**user.model_dump())
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"New user created with id: {new_user.id}")
        return new_user
    
    except IntegrityError as e:
        await db.rollback()
        logger.info(f"Integrity error during user creating {str(e)}")
        raise EmailAlreadyExistsException("Email already exist")
        
    
    except Exception as e:
        await db.rollback()
        logger.exception("Unexpected error during user creation.")
        raise   # Now, global exception handler will catch it
        
@router.post("/signin")
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    
    try:
        statement = select(models.User).where(models.User.email == user_credentials.username)
    
        user = await db.execute(statement)
        
        user = user.scalar_one_or_none()
        
        if user is None:
            raise UserNotFoundException(f"User with email: {user_credentials.username} not found")
        
        if not password_encoder.verify(user_credentials.password, user.password):
            raise InvalidPasswordException("Invalid Credentials")
        
        access_token = oauth2.create_access_token(data={"user_id": user.id, "role": user.role.value})
        refresh_token = oauth2.create_refresh_token(data={"user_id": user.id, "role": user.role.value})
    except Exception as e:
        raise
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest, 
    background_tasks: BackgroundTasks, 
    db: AsyncSession = Depends(get_db)
    ):
    
    """Request for Password Reset"""
    
    result = await db.execute(select(models.User).where(models.User.email == request.email))
    
    user = result.scalar_one_or_none()
    
    if not user:
        raise UserNotFoundException("User doesn't exist")
    
    PASSWORD_RESET_TOKEN_EXPIRE_TIME = settings.password_reset_token_expire_minutes
    
    # Generate reset token
    reset_token = generate_reset_token()
    expiration_time = datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_TIME)
    
    # save token
    token_obj = ResetPasswordToken(
        user_id = user.id,
        token = reset_token,
        expiration_time = expiration_time
    )
    
    db.add(token_obj)
    await db.commit()
    
    # send email
    background_tasks.add_task(send_password_reset_email,user.email,user.name,reset_token)
    return {"message": f"token has sent to your email: {request.email} "}
    
    
@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Reset password using token"""
    result = await db.execute(
        select(ResetPasswordToken)
        .where(ResetPasswordToken.token == request.token)
        .where(ResetPasswordToken.used == False)
        .where(ResetPasswordToken.expiration_time > datetime.now(timezone.utc))
    )
    token_obj = result.scalar_one_or_none()
    
    if not token_obj:
        raise InvalidTokenException("Invalid or expired token")
    
    # Update password
    hashed_password = password_encoder.hash(request.new_password)
    await db.execute(
        update(models.User)
        .where(models.User.id == token_obj.user_id)
        .values(password=hashed_password)
    )
    
    # Mark token as used
    await db.execute(
        update(ResetPasswordToken)
        .where(ResetPasswordToken.id == token_obj.id)
        .values(used=True)
    )
    
    await db.commit()
    
    return {"message": "Password reset successfully"}