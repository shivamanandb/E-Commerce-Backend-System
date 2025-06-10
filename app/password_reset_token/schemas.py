from pydantic import BaseModel, EmailStr

class ForgetPasswordRequest(BaseModel):
    email: EmailStr
