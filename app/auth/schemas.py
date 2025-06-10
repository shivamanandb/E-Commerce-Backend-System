from pydantic import BaseModel, EmailStr, field_validator, Field
from ..exceptions import InvalidNameException
from datetime import datetime

class CreateUser(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str
    
    @field_validator('name')
    @classmethod
    def check_for_valid_name(cls, value):
        if not value.replace(" ", "").isalpha():
            raise InvalidNameException("Name is not valid")
        return value
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return value
    
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime
    
    class Config:
        from_attribute = True
        
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    
from pydantic import BaseModel, EmailStr, field_validator

class ForgetPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return value