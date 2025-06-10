from pydantic import BaseModel, condecimal
from datetime import datetime

class CreateProduct(BaseModel):
    name: str
    description: str
    price: condecimal(decimal_places=2, ge=0)
    stock: int
    category: str
    
class Product(CreateProduct):
    id: int
    image_url: str
    
class ProductDetails(Product):
    is_active: bool = True
    created_at:datetime