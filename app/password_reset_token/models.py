from sqlalchemy import Column, Integer, ForeignKey, Boolean, String
from decimal import Decimal
from sqlalchemy.sql.sqltypes import TIMESTAMP, Numeric
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from ..configuration.database import Base

class ResetPasswordToken(Base):
    __tablename__ = "reset_password_token"
    
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, nullable=False, unique=True)
    expiration_time = Column(TIMESTAMP(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    
    user = relationship("User", back_populates="password_reset_tokens")
    