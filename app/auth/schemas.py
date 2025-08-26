from pydantic import BaseModel, EmailStr, field_validator, Field
from exceptions import InvalidNameException
from datetime import datetime
from typing import Literal

class CreateUser(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Full name of user (2-50 Characters)")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters long")
    role: Literal["admin", "user"] = Field(..., description="Person can register as an `admin` or `user`")
    
    @field_validator('name')
    @classmethod
    def check_for_valid_name(cls, value):
        if not value.replace(" ", "").isalpha():
            raise InvalidNameException("Name is not valid. Only alphabetic characters and spaces are allowed.")
        return value
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, value):
        # Add simple security rule: must contain at least one letter and one digit
        if len(value) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one letter and one number")
        return value
    
    class Config:
        title = "CreateUserInput"
        description = "Model for requesting input to create Users."


class UserResponse(BaseModel):
    id: int = Field(..., description="Unique id for the user")
    name: str = Field(..., description="Full name of user")
    email: EmailStr = Field(..., description="User's email ID")
    role: str = Field(..., description="User role: either `user` or `admin`")
    created_at: datetime = Field(..., description="Timestamp when the user was created")
    
    class Config:
        title = "UserResponseOutput"
        from_attributes = True


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Email to send password reset token")
    
    class Config:
        title = "ForgotPasswordRequestInput"


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Unique reset token")
    new_password: str = Field(..., min_length=6, description="New password to replace old one")
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one letter and one number")
        return value
    
    class Config:
        title = "ResetPasswordRequestInput"
