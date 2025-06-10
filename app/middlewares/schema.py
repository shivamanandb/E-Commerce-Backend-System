from pydantic import BaseModel
from ..auth.models import UserRole

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    id: int  
    role: UserRole