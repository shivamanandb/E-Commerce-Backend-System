from sqlalchemy import Column, String, Integer, Enum, ForeignKey, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from ..configuration.database import Base
import enum  # <-- For Python Enum

# Enum for role values
class UserRole(enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, server_default="user")  # Default role = 'user'
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    
    cart_items = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    password_reset_tokens = relationship("ResetPasswordToken", back_populates="user")
    
    
# Reset Password Token 
class ResetPasswordToken(Base):
    __tablename__ = "reset_password_token"
    
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, nullable=False, unique=True)
    expiration_time = Column(TIMESTAMP(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    
    user = relationship("User", back_populates="password_reset_tokens")