from fastapi import FastAPI
from .auth import models as auth_model
from .cart import models as cart_model
from .orderItems import models as orderItems_model
from .orders import models as orders_model
from .password_reset_token import models as reset_token_model
from .auth import routes as auth 
from .cart import routes as cart 
from .orderItems import routes as orderItems 
from .orders import routes as orders
from .products import routes as products 
from .password_reset_token import routes as reset_token
 

from .configuration.database import engine

app = FastAPI(
    title="E-commerce Backend API",
    description="Comprehensive e-commerce backend system with FastAPI",
)

auth_model.Base.metadata.create_all(bind=engine)
cart_model.Base.metadata.create_all(bind=engine)
orderItems_model.Base.metadata.create_all(bind=engine)
orders_model.Base.metadata.create_all(bind=engine)
reset_token_model.Base.metadata.create_all(bind=engine)

app.include_router(auth.router,        prefix="/auth",        tags=["Auth"])
app.include_router(products.router,    prefix="/products",    tags=["Products"])
app.include_router(cart.router,        prefix="/cart",        tags=["Cart"])
app.include_router(orders.router,      prefix="/orders",      tags=["Orders"])
app.include_router(orderItems.router,  prefix="/orderItems",  tags=["Order Items"])
app.include_router(reset_token.router, prefix="/reset",       tags=["Reset Password Token"])

@app.get("/")
async def root():
    return {'message': 'hello world'}