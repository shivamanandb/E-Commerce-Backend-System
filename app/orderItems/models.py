from sqlalchemy import Column, Integer, String, ForeignKey
from decimal import Decimal
from sqlalchemy.sql.sqltypes import TIMESTAMP, Numeric
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from ..configuration.database import Base

class OrderItems(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price_at_purchase = Column(Numeric(10, 2), nullable=False)  
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
