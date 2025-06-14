from pydantic import BaseModel, condecimal, Field
from datetime import datetime


class ProductViewNormalUser(BaseModel):
    """
    Schema for products as viewed by a normal user in the product listing.
    """
    id: int = Field(..., description="Unique identifier of the product")
    name: str = Field(..., description="Name of the product", example="Wireless Mouse")
    price: condecimal(decimal_places=2, ge=0) = Field(..., description="Price of the product", example=499.99)
    image_url: str = Field(..., description="URL of the product image")
    category: str = Field(..., description="Product category", example="Electronics")

    class Config:
        title = "ProductViewNormalUser"
        from_attributes = True


class ProductViewNormalUserDetailed(ProductViewNormalUser):
    """
    Extended schema including product description, used for detailed views.
    """
    description: str = Field(..., description="Detailed description of the product", example="Ergonomic wireless mouse with 3 adjustable DPI levels.")

    class Config:
        title = "ProductViewNormalUserInDetail"
        from_attributes = True
