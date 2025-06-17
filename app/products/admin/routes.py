from fastapi import APIRouter, File, UploadFile, Form, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, asc, delete, desc, update
from typing import List, Optional
from .. import models
from ...auth import models as user_model
from ...configuration.database import get_db
from ...utils.image_uploader import upload_image_to_cloudinary 
from ...configuration.config import settings
from . import schemas
from ...middlewares import oauth2
from ...exceptions import ProductNotFoundException, InvalidImageTypeException, GeneralException
from ...orders.models import OrderItems
import tempfile
import logging
import os

# Initialize logger
logger = logging.getLogger(__name__)

# Create API router for product-related operations
router = APIRouter()

# -----------------------------
# CREATE PRODUCT (Admin API)
# -----------------------------
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ProductOutput, tags=["Product - Admin APIs"])
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    category: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(oauth2.get_current_user)
):
    """
    Create a new product with image. Uploads image to Cloudinary and saves product details in database.
    """
    
    
    try:
        
        # check whether content type is valid or not
        if not file.content_type.startswith('image/'):
            raise InvalidImageTypeException("Only image file is allowed")
        
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # Upload image to Cloudinary
        upload_result = await upload_image_to_cloudinary(tmp_path, folder=settings.folder_name)
        image_url = upload_result.get("secure_url")

        # Cleanup temporary file
        try:
            os.remove(tmp_path)
        except Exception as e:
            logger.warning(f"Temporary file cleanup failed: {e}")

        # Create and save new product
        new_product = models.Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category,
            user_id=current_user.id,
            image_url=image_url
        )

        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)

        return new_product

    except InvalidImageTypeException:
        raise

    except Exception as e:
        logger.error(f"Product creation failed: {str(e)}")
        raise GeneralException(status_code=500, message="Internal Server Error during product creation")


# -----------------------------
# GET PRODUCTS (Admin API)
# -----------------------------
@router.get("/", response_model=List[schemas.ProductOutput], tags=["Product - Admin APIs"])
async def get_products(
    db: AsyncSession = Depends(get_db), 
    limit: int = 10, 
    skip: int = 0, 
    min_price: int = 0,
    max_price: Optional[int] = None, 
    sort_by: Optional[str] = "id", 
    category: Optional[str] = None
):
    """
    Retrieve paginated and filtered list of products. Supports filtering by price, category, and sorting.
    """
    statement = select(models.Product)
    
    filters = [models.Product.price >= min_price, models.Product.is_active == True]
    
    if max_price is not None:
        filters.append(models.Product.price <= max_price)
    
    if category:
        filters.append(models.Product.category == category)
    
    if filters:
        statement = statement.where(and_(*filters))
        
    if sort_by in ["id", "price", "stock", "created_at"]:
        statement = statement.order_by(getattr(models.Product, sort_by))
    else:
        statement = statement.order_by(models.Product.id)
        
    statement = statement.limit(limit).offset(skip)
    
    result = await db.execute(statement)
    
    return result.scalars().all()


# -----------------------------
# SEARCH PRODUCTS (Admin API)
# -----------------------------
@router.get("/search", response_model=List[schemas.ProductOutput], tags=["Product - Admin APIs"])
async def product_search(
    db: AsyncSession = Depends(get_db), 
    product_name: Optional[str] = None
):
    """
    Search products by keyword match on product name.
    """
    statement = select(models.Product).where(models.Product.is_active == True)

    if product_name:
        statement = statement.where(models.Product.name.ilike(f"%{product_name}%"))

    result = await db.execute(statement)
    return result.scalars().all()


# -------------------------------
# GET YOUR PRODUCTS (ADMIN API)
# -------------------------------
@router.get("/all", response_model=List[schemas.ProductOutput], tags=["Product - Admin APIs"])
async def your_products(
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(oauth2.get_current_user)
):
    """ 
    Get only those product details that is created by their own. 
    """
    statement = await db.execute(
        select(models.Product)
        .where(models.Product.user_id == current_user.id,
                models.Product.is_active == True
            )
    )
    
    products = statement.scalars().all()
    
    if not products:
        raise ProductNotFoundException(f"No product found")
    
    return products


# -----------------------------
# GET PRODUCT BY ID (Admin API)
# -----------------------------
@router.get("/{id}", response_model=schemas.ProductDetailsOutput, tags=["Product - Admin APIs"])
async def product_by_id(id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a single product by ID including all metadata.
    """
    statement = select(models.Product).where(models.Product.id == id, models.Product.is_active == True)
    result = await db.execute(statement)
    product = result.scalar_one_or_none()

    if not product:
        raise ProductNotFoundException(f"Product not found with ID: {id}")

    return product


# -----------------------------
# DELETE PRODUCT BY ID (Admin API)
# -----------------------------

@router.delete("/{id}", tags=["Product - Admin APIs"])
async def delete_product_by_id(
    id: int, db: AsyncSession = Depends(get_db), 
    current_user: user_model.User = Depends(oauth2.get_current_user)
):
    """
    Delete a product from the database using its ID.
    Basic Idea is that if product is ordered at least one time and if is it deleted from DB
    then the people will face issue to see their ordered product in their order history.
    Now, I come up with the idea that I created an attribute, named, is_active. if a product 
    is ordered at least one time and in future I admin want to delete such product then its
    deletion will be soft deleted, means only is_active value will false.Product will persist 
    in DB but no one will allow to access. and if product didn't order even a single time, it 
    can be deleted easily.
    """
    statement = select(models.Product).where(
        models.Product.id == id,
        models.Product.is_active == True
    )
    
    result = await db.execute(statement)
    product = result.scalar_one_or_none()

    if not product:
        raise ProductNotFoundException(f"Product not found with ID: {id}")
    
    if product.user_id != current_user.id:
        raise GeneralException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            message="Only the creator admin is allowed to delete this product."
        )
    
    # check whether product has been ordered earlier or not
    is_order = await db.execute(select(OrderItems).where(OrderItems.product_id == id))
    
    is_order = is_order.scalar_one_or_none()
    
    if not is_order:
        delete_statement = delete(models.Product).where(models.Product.id == id)
        await db.execute(delete_statement)
    
    else:
        await db.execute(
            update(models.Product)
            .where(models.Product.id == id)
            .values(is_active=False)
        )
        
        
    await db.commit()

    return {"message": "Product deleted successfully"}

# -----------------------------
# UPDATE PRODUCT BY ID (Admin API)
# -----------------------------
@router.put("/{id}", response_model=schemas.ProductDetailsOutput, status_code=status.HTTP_200_OK, tags=["Product - Admin APIs"])
async def update_product(
    id: int,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    category: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(oauth2.get_current_user)
):
    """
    Update a product's information. Optionally upload a new image.
    """
    stmt = select(models.Product).where(models.Product.id == id, models.Product.is_active == True)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise ProductNotFoundException(f"Product not found with ID: {id}")
    
    if product.user_id != current_user.id:
        raise GeneralException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="only creator admin is allowed to update this product."
        )

    if file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        upload_result = await upload_image_to_cloudinary(tmp_path, folder=settings.folder_name)
        product.image_url = upload_result.get("secure_url")

        try:
            os.remove(tmp_path)
        except Exception as e:
            logger.warning(f"Temp file deletion failed: {e}")

    product.name = name
    product.description = description
    product.price = price
    product.stock = stock
    product.category = category

    await db.commit()
    await db.refresh(product)

    return product


