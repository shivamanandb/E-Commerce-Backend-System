from sqlalchemy import Column, String, Integer, Enum, ForeignKey, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from ..configuration.database import Base
import enum

# -------------------------------
# ENUM DECLARATIONS
# -------------------------------

class UserRole(enum.Enum):
    """
    Enumeration for user roles.
    Ensures only allowed roles can be assigned (e.g., 'user' or 'admin').
    """
    user = "user"
    admin = "admin"


# -------------------------------
# USER MODEL
# -------------------------------

class User(Base):
    """
    Represents a registered user in the system.

    Relationships:
    - One-to-many with Cart (User → CartItems)
    - One-to-many with Order (User → Orders)
    - One-to-many with ResetPasswordToken
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)

    # Email must be unique to avoid duplicate accounts
    email = Column(String, unique=True, nullable=False)

    # Hashed password is stored
    password = Column(String, nullable=False)

    # Enum-based role enforcement with default value 'user'
    role = Column(Enum(UserRole), nullable=False, server_default="user")

    # Timestamp of user creation, uses PostgreSQL's now()
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # Relationship definitions
    cart_items = relationship(
        "Cart", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )

    orders = relationship(
        "Order", 
        back_populates="user"
    )

    password_reset_tokens = relationship(
        "ResetPasswordToken", 
        back_populates="user"
    )


# -------------------------------
# RESET PASSWORD TOKEN MODEL
# -------------------------------

class ResetPasswordToken(Base):
    """
    Stores unique password reset tokens for each user.
    Tokens are single-use and expire after a set duration.

    Foreign Keys:
    - user_id → users.id (CASCADE delete ensures cleanup on user deletion)
    """
    __tablename__ = "reset_password_token"

    id = Column(Integer, primary_key=True, nullable=False)

    # Foreign key to User
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )

    # Unique token value (UUID)
    token = Column(String, nullable=False, unique=True)

    # Timestamp when token becomes invalid
    expiration_time = Column(TIMESTAMP(timezone=True), nullable=False)

    # Flag to check if token has already been used
    used = Column(Boolean, default=False, nullable=False)

    # Relationship to parent user
    user = relationship("User", back_populates="password_reset_tokens")
