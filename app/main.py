from fastapi import FastAPI, Depends
from .auth import models as auth_model
from .cart import models as cart_model
from .orderItems import models as orderItems_model
from .orders import models as orders_model
from .products import models as products_model
from .password_reset_token import models as reset_token_model
from .middlewares import routes as oauth2
from .auth import routes as auth 
from .cart import routes as cart 
from contextlib import asynccontextmanager
from .orderItems import routes as orderItems
from .configuration import cloudinary 
from .orders import routes as orders
from .products.admin import routes as products_admin_routes
from .products.user import routes as products_user_routes
from .password_reset_token import routes as reset_token
from .global_exception_handler import add_exception_handlers 
from .configuration.database import engine
from .dependency import require_admin, require_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="E-commerce Backend API",
    description="Comprehensive e-commerce backend system with FastAPI",
    lifespan=lifespan
)

# Register global exception handlers
add_exception_handlers(app)

# assuming you have AsyncEngine 'engine' and Base declarative model 'Base'

async def init_db():
    async with engine.begin() as conn:
        # create tables for all metadata objects (if multiple bases)
        await conn.run_sync(auth_model.Base.metadata.create_all)
        await conn.run_sync(cart_model.Base.metadata.create_all)
        await conn.run_sync(orderItems_model.Base.metadata.create_all)
        await conn.run_sync(orders_model.Base.metadata.create_all)
        await conn.run_sync(products_model.Base.metadata.create_all)
        await conn.run_sync(reset_token_model.Base.metadata.create_all)


app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(products_admin_routes.router, prefix="/admin/products", tags=["Products"], dependencies=[Depends(require_admin)])
app.include_router(products_user_routes.router, prefix="/products", tags=["Products"], dependencies=[Depends(require_user)])
app.include_router(cart.router,        prefix="/cart",        tags=["Cart"])
app.include_router(orders.router,      prefix="/orders",      tags=["Orders"])
app.include_router(orderItems.router,  prefix="/orderItems",  tags=["Order Items"])
app.include_router(reset_token.router, prefix="/reset",       tags=["Reset Password Token"])
app.include_router(cloudinary.router,  prefix="/upload",      tags=["Reset Password Token"])
app.include_router(oauth2.router, tags=["Refresh Token"])

@app.get("/")
async def root():
    return {'message': 'hello world'}