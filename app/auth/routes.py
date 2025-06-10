from fastapi import APIRouter, status, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .. import exceptions
from ..middlewares import oauth2
from . import schemas, models
import logging
from ..configuration import logger_config
from ..exceptions import EmailAlreadyExistsException, UserNotFoundException, InvalidPasswordException
from sqlalchemy.exc import IntegrityError
from ..configuration.database import get_db
from ..utils import password_encoder
from . import models
from ..utils import password_encoder 


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