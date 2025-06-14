from pydantic import BaseModel, Field

class CartData(BaseModel):
    product_id: int = Field(...,description="Unique id of product")
    quantity: int = Field(..., description="Quantity of particular product in the Cart")
    
    class Config:
        title="CartDataInput"

class ProductQuantity(BaseModel):
    quantity: int = Field(..., description="Quantity of product for quantity updation")

    class Config:
        title="ProductQuantityInput"
        description="Model for Product Quantity updation"
class CartProduct(BaseModel):
    id: int = Field(..., description="Unique id of Product")
    name: str = Field(..., description="Name of the Product")
    image_url: str = Field(..., description="Url of Image that is uploaded on cloudinary")
    price: float = Field(..., description="Price of the Product")
    quantity: int = Field(..., description="Added quantity of Product in cart")
    subtotal: float = Field(..., description="Subtotal of product calculated using price and quantity")

    class Config:
        title="CartProductInput -> No DB interaction"

class CartResponse(BaseModel): 
    items: list[CartProduct] = Field(..., description="Detailed View of Product")
    total_amount: float = Field(..., description="Total amount (sum of subtotals)")

    class Config:
        title="CartResponseOutput -> No DB interaction"
    
class CheckOutAddress(BaseModel): 
    address: str = Field(..., description="Address for Product Checkout")
    
    class Config:
        title="CheckOutAddressInput"