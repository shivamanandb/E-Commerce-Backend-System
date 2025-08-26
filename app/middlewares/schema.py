from pydantic import BaseModel, Field
from auth.models import UserRole


class Token(BaseModel):
    """
    Represents the structure of JWT tokens returned to the client
    after successful authentication or refresh.
    """
    access_token: str = Field(..., description="JWT access token used for authentication (short-lived)")
    refresh_token: str = Field(..., description="JWT refresh token used to obtain a new access token (long-lived)")
    token_type: str = Field("bearer", description="Token type: always 'bearer' for JWT usage")

    class Config:
        title = "TokenDataOutput"
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """
    Represents the extracted payload from a decoded JWT token.
    This is used internally for verifying and identifying the user.
    """
    id: int = Field(..., description="User's unique identifier from the database")
    role: UserRole = Field(..., description="User's role — typically 'admin' or 'user'")

    class Config:
        title = "TokenPayloadDecoded"
        json_schema_extra = {
            "example": {
                "id": 1,
                "role": "user"
            }
        }
