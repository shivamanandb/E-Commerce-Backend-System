# from pydantic import BaseModel
# from ..products.models import Product

# class CartResponse(CartData):
#     product_name: str
#     product_description: str
#     product_price: int
#     product_category: str
#     product_image: str    

from pydantic import BaseModel

class CartData(BaseModel):
    product_id: int
    quantity: int

class ProductQuantity(BaseModel):
    quantity: int

class CartProduct(BaseModel):
    id: int
    name: str
    image_url: str
    price: float
    quantity: int
    subtotal: float

    # class Config:
    #     orm_mode = True

class CartResponse(BaseModel):
    items: list[CartProduct]
    total_amount: float

class CheckOutAddress(BaseModel):
    address: str