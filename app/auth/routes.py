from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from .. import exceptions
from . import schemas
import logging
from ..configuration import logger_config
from ..configuration.database import get_db


router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.CreateUser, db: Session = Depends(get_db)):
    """
    Create a user after validating details and then hashing password
    """
    
    # step 1:- All required details must be filled
    # step 2:- check email is valid or not
    # 
    # try:
    #     hashed_password 
    