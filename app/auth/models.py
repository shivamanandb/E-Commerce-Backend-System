from sqlalchemy import Column, String, Integer, Enum
from sqlalchemy.sql.expression import text
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
    
    
