from sqlalchemy import Column, Integer, String, Float, Boolean, Numeric, CheckConstraint
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from ..configuration.database import Base
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)    
    price = Column(Numeric(10,2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    category = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    cart_items = relationship("Cart", back_populates="product")
    order_items = relationship("OrderItems", back_populates="product")
    
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_price_positive'),
    )
# If product has not ordered even a single time then I can delete it easily,
# but if someone has ordered then it can't be deleted. In this case, we will 
# discontinue that product, by putting is_active = False