from pydantic import BaseModel, condecimal
from datetime import datetime

class ProductViewNormalUser(BaseModel):
    name: str
    price: condecimal(decimal_places=2, ge=0)
    image_url: str

class ProductViewNormalUserDetailed(ProductViewNormalUser):
    description: str
    category: str
    