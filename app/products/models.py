from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from ..configuration.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    product = relationship("Cart", back_populates="products")
    orderItems = relationship("OrderItems", back_populates="products")
# If product has not ordered even a single time then I can delete it easily,
# but if someone has ordered then it can't be deleted. In this case, we will 
# discontinue that product, by putting is_active = False