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