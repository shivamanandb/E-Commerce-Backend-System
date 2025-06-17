from pydantic import BaseModel, condecimal, Field
from datetime import datetime

# ------------------------------
# Create Product Input Schema
# ------------------------------
class CreateProductInput(BaseModel):
    """
    Input schema for creating a new product.
    """
    name: str = Field(..., description="Name of the product")
    description: str = Field(..., description="Detailed description of the product")
    price: condecimal(decimal_places=2, ge=0) = Field(..., description="Selling price of the product (>= 0)")
    stock: int = Field(..., ge=0, description="Available stock quantity (>= 0)")
    category: str = Field(..., description="Category the product belongs to")

    class Config:
        title = "CreateProductInput"


# ------------------------------
# Product Output Schema
# ------------------------------
class ProductOutput(CreateProductInput):
    """
    Output schema for listing products (e.g., GET /products).
    Inherits all fields from CreateProductInput and adds ID and image URL.
    """
    id: int = Field(..., description="Unique identifier of the product")
    image_url: str = Field(..., description="URL of the product image hosted on cloud")

    class Config:
        from_attributes = True
        title = "ProductOutput"
        

# ------------------------------
# Product Detailed Output Schema
# ------------------------------
class ProductDetailsOutput(ProductOutput):
    """
    Detailed output schema for a single product (e.g., GET /products/{id}).
    Adds creation timestamp and activation status.
    """
    created_at: datetime = Field(..., description="Timestamp when the product was created")

    class Config:
        from_attributes = True
        title = "ProductDetailsOutput"
    
