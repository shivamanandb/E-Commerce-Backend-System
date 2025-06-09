from sqlalchemy import Column, Integer, ForeignKey, Enum
from decimal import Decimal
from sqlalchemy.sql.sqltypes import TIMESTAMP, Numeric
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from ..configuration.database import Base
import enum

# Define Python Enum for order status
class OrderStatus(enum.Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_amount = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    order_items = relationship("OrderItems", back_populates="order")