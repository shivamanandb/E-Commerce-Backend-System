from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from ..configuration.database import Base
from ..products.models import Product


# -------------------------------
# CART MODEL
# -------------------------------

class Cart(Base):
    """
    Represents an item added to a user's shopping cart.
    
    A cart item is linked to both a user and a product, and includes the selected quantity.
    Deleting a user or product cascades and removes the associated cart entries.

    Relationships:
    - Many-to-One with User
    - Many-to-One with Product
    """
    __tablename__ = "cart_items"

    # Primary key for each cart item
    id = Column(Integer, primary_key=True, nullable=False)

    # Reference to the user who owns this cart item
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Reference to the product added to the cart
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )

    # Number of units of the product added to the cart
    quantity = Column(Integer, default=1, nullable=False)

    # Timestamp for when the cart item was created
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text('now()')
    )

    # Relationships (bidirectional)
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

    