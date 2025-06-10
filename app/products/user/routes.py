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

@router.get("/", response_model=List[schemas.ProductViewNormalUser])
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
        
    if sort_by in ["price", "stock", "created_at"]:
        statement = statement.order_by(asc(getattr(models.Product, sort_by)))
    else:
        statement = statement.order_by(models.Product.id) # by default
        
    statement = statement.limit(limit).offset(skip)
    
    result = await db.execute(statement)
    
    return result.scalars().all()

@router.get("/search", response_model=List[schemas.ProductViewNormalUser])
async def product_search(db: AsyncSession = Depends(get_db), keyword : Optional[str] = None):
    
    statement = select(models.Product)
    
    if keyword is not None:
        statement = statement.where(models.Product.name.contains(keyword))
    
    products = await db.execute(statement)
    
    return products.scalars().all()

@router.get("/{id}", response_model=schemas.ProductViewNormalUserDetailed)
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