from sqlalchemy import (
    Column, Integer, ForeignKey, Enum, CheckConstraint, String,
    TIMESTAMP, Numeric, text
)
from sqlalchemy.orm import relationship
from decimal import Decimal
from configuration.database import Base
import enum

# ---------------------------------------------------------
# ENUM: Order Status Values
# ---------------------------------------------------------

class OrderStatus(enum.Enum):
    """
    Enum representing the current state of an order.
    """
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"

# ---------------------------------------------------------
# TABLE: orders
# ---------------------------------------------------------

class Order(Base):
    """
    Table representing an order placed by a user.
    
    Fields:
    - user_id: FK to the user who placed the order.
    - total_amount: Pre-calculated at time of checkout.
    - address: Shipping address for the order.
    - status: Current order status (pending/paid/cancelled).
    - created_at: Timestamp of order placement.
    
    Relationships:
    - user: Links to User table.
    - order_items: List of OrderItems in this order.
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    total_amount = Column(
        Numeric(10, 2),
        default=Decimal('0.00'),
        nullable=False
    )

    address = Column(String, nullable=False)

    status = Column(
        Enum(OrderStatus),
        default=OrderStatus.pending,
        nullable=False
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    # Relationships
    user = relationship("User", back_populates="orders")
    order_items = relationship(
        "OrderItems",
        back_populates="order"
    )

# ---------------------------------------------------------
# TABLE: order_items
# ---------------------------------------------------------

class OrderItems(Base):
    """
    Table representing individual product entries in an order.
    
    Fields:
    - order_id: FK to parent order.
    - product_id: FK to purchased product.
    - quantity: Quantity of the product.
    - price_at_purchase: Price at time of order for history tracking.
    - created_at: When the item was added to order.

    Constraints:
    - quantity > 0
    - price_at_purchase >= 0
    
    Relationships:
    - order: Parent Order.
    - product: Purchased Product.
    """
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(Integer, nullable=False, default=1)

    price_at_purchase = Column(Numeric(10, 2), nullable=False)

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_quantity_positive"),
        CheckConstraint("price_at_purchase >= 0", name="check_price_non_negative"),
    )
