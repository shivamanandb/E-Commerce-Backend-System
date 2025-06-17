from sqlalchemy import Column,Integer, String, Numeric, TIMESTAMP, CheckConstraint, Boolean, text, ForeignKey

from sqlalchemy.orm import relationship
from ..configuration.database import Base


class Product(Base):
    """
    Represents a product available for purchase on the platform.

    - Products can be soft-deleted using the 'is_active' flag.
    - Deletion is restricted if the product has been ordered (enforced in business logic).
    
    Relationships:
    - One-to-Many with Cart
    - One-to-Many with OrderItems
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, nullable=False)

    # Name of the product
    name = Column(String, nullable=False, index=True)

    # Description of the product
    description = Column(String, nullable=False)

    # Price per unit (min ₹1.00)
    price = Column(Numeric(10, 2), nullable=False)

    # Number of units available in inventory
    stock = Column(Integer, nullable=False, default=0)

    # Category to which this product belongs
    category = Column(String, nullable=False, index=True)

    # Optional image URL for the product
    image_url = Column(String, nullable=True)
    
    # Admin User id who is creating particular product
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Soft delete flag to mark product as inactive/discontinued
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamp of product creation
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()')
    )

    # Relationships
    cart_items = relationship("Cart", back_populates="product")
    order_items = relationship("OrderItems", back_populates="product")
    user = relationship("User", back_populates="product")

    # Constraints to ensure data integrity
    __table_args__ = (
        CheckConstraint('price >= 1', name='check_price_greater_than_1'),
        CheckConstraint('stock >= 0', name='check_stock_positive'),
    )
    
