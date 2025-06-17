from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager

# Import all SQLAlchemy models to register them with metadata
from .auth import models as auth_model
from .cart import models as cart_model
from .orders import models as orderItems_model
from .orders import models as orders_model
from .products import models as products_model
from .auth import models as reset_token_model

# Import route modules
from .auth import routes as auth
from .cart import routes as cart
from .orders import routes as orderItems
from .orders import routes as orders
from .products.admin import routes as products_admin_routes
from .products.user import routes as products_user_routes
from .middlewares import routes as oauth2

# Import configuration utilities
from .configuration import cloudinary
from .configuration.database import engine

# Import shared utilities
from .global_exception_handler import add_exception_handlers 
from .dependency import require_admin, require_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan event handler.
    This will run once at startup and is the right place to initialize database schemas, external services, etc.
    """
    await init_db()  # Initialize the database (create tables)
    yield  # Control passes to the application after this


# Initialize FastAPI application with custom metadata and lifespan handler
app = FastAPI(
    title="E-commerce Backend API",
    description="E-commerce backend system with FastAPI",
    lifespan=lifespan
)


# Function to initialize DB schema by creating tables
# If multiple Base objects are defined (per module), we must call `create_all` on each
async def init_db():
    async with engine.begin() as conn:
        # Create all tables (only if they don’t exist)
        await conn.run_sync(auth_model.Base.metadata.create_all)
        await conn.run_sync(cart_model.Base.metadata.create_all)
        await conn.run_sync(orderItems_model.Base.metadata.create_all)
        await conn.run_sync(orders_model.Base.metadata.create_all)
        await conn.run_sync(products_model.Base.metadata.create_all)
        await conn.run_sync(reset_token_model.Base.metadata.create_all)


# Register centralized/global exception handlers
add_exception_handlers(app)


# ---------------------------
#         ROUTING
# ---------------------------

# Authentication APIs (Register, Login, Forgot Password, etc.)
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

# Admin-only product management APIs
app.include_router(
    products_admin_routes.router,
    prefix="/admin/products",
    tags=["Product - Admin APIs"],
    dependencies=[Depends(require_admin)]  # Ensures only admins can access
)

# Public/product browsing and purchase-related APIs (Requires logged-in user)
app.include_router(
    products_user_routes.router,
    prefix="/products",
    tags=["Product - User APIs"],
    dependencies=[Depends(require_user)]
)

# Shopping cart operations for users
app.include_router(
    cart.router,
    prefix="/cart",
    tags=["Cart - User APIs"],
    dependencies=[Depends(require_user)]
)

# Order creation and viewing (user-specific)
app.include_router(
    orders.router,
    prefix="/orders",
    tags=["Orders - User APIs"],
    dependencies=[Depends(require_user)]
)

# Refresh token route
app.include_router(
    oauth2.router,
    tags=["Refresh Token"]  # Note: this may be too strict; review
)


# --------------------------
#  APPLICATION STARTUP 
# ---------------------------

@app.get("/")
async def root():
    """
    check endpoint to verify the application is running.
    """
    return {'message': 'hello world'}
