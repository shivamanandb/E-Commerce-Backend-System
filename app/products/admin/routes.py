from fastapi import APIRouter, File, UploadFile, Form, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, asc, desc, delete
from typing import List, Optional
from .. import models
from ...configuration.database import get_db
from ...utils.image_uploader import upload_image_to_cloudinary 
from ...configuration.config import settings
from . import schemas
from ...exceptions import ProductNotFoundException
import tempfile
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Product)
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    category: str = Form(...),
    file: UploadFile = File(...),  # image file
    db: AsyncSession = Depends(get_db)
):
    try:        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # Upload image to Cloudinary
        upload_result = await upload_image_to_cloudinary(tmp_path, folder=settings.folder_name)
        image_url = upload_result.get("secure_url")

        # Create product model
        new_product = models.Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category,
            image_url=image_url
        )

        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
    except Exception as e:
        logger.info(f"Unexpected Error during product creation {str(e)}")
        raise 
        
    return new_product

@router.get("/", response_model=List[schemas.Product])
async def get_product(db: AsyncSession = Depends(get_db), 
                    limit: int = 10, skip: int = 0, min_price: int = 0,
                    max_price : int = None, sort_by : Optional[str] = "id", category : Optional[str] = None):
    
    statement = select(models.Product)
    
    filters = [models.Product.price >= min_price]
    
    if max_price is not None:
        filters.append(models.Product.price <= max_price)
    
    if category:
        filters.append(models.Product.category == category)
    
    if filters:
        statement = statement.where(and_(*filters))
        
    if sort_by in ["id", "price", "stock", "created_at"]:
        statement = statement.order_by(asc(getattr(models.Product, sort_by)))
    else:
        statement = statement.order_by(models.Product.id) # by default
        
    statement = statement.limit(limit).offset(skip)
    
    result = await db.execute(statement)
    
    return result.scalars().all()

@router.get("/search", response_model=List[schemas.Product])
async def product_search(db: AsyncSession = Depends(get_db), keyword : Optional[str] = None):
    
    statement = select(models.Product)
    
    if keyword is not None:
        statement = statement.where(models.Product.name.contains(keyword))
    
    products = await db.execute(statement)
    
    return products.scalars().all()

@router.get("/{id}", response_model=schemas.ProductDetails)
async def product_by_id(id: int, db: AsyncSession = Depends(get_db)):
    
    try:
        statement = select(models.Product).where(models.Product.id == id)
    
        result = await db.execute(statement)
        
        product = result.scalar_one_or_none()
        
        if product is None:
            raise ProductNotFoundException(f"Product is not listed here with product_id: {id}")
    except Exception as e:
        raise

    return product
    
@router.delete("/{id}")
async def delete_product_by_id(id: int, db: AsyncSession = Depends(get_db)):
    try:
        
        statement = select(models.Product).where(models.Product.id == id)
        result = await db.execute(statement)
        product = result.scalar_one_or_none()
        if product is None:
            raise ProductNotFoundException(f"Product is not listed here with product_id: {id}")
        
        statement = delete(models.Product).where(models.Product.id == id)
        await db.execute(statement) 
        await db.commit()
            
    except Exception as e:
        raise

    return {"message": "Product Deleted Successfully"}


@router.put("/{id}")
async def update_product(
    id: int,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    category: str = Form(...),
    file: Optional[UploadFile] = File(None),  # Optional image
    db: AsyncSession = Depends(get_db)
):
    
    stmt = select(models.Product).where(models.Product.id == id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if product is None:
        raise ProductNotFoundException(f"Product is not listed here with product_id: {id}")

    image_url = product.image_url  # default to old image

    if file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        upload_result = await upload_image_to_cloudinary(tmp_path, folder=settings.folder_name)
        image_url = upload_result.get("secure_url")

    product.name = name
    product.description = description
    product.price = price
    product.stock = stock
    product.category = category
    product.image_url = image_url

    await db.commit()
    await db.refresh(product)

    return {
        "message": "Product updated successfully",
        "product": {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "category": product.category,
            "image_url": product.image_url,
            "created_at": product.created_at,
            "is_active": product.is_active
        }
    }
