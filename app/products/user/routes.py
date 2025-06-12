from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, asc
from typing import List, Optional
from .. import models
from ...configuration.database import get_db
from . import schemas
from ...exceptions import ProductNotFoundException
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Create router for user-facing product APIs
router = APIRouter()


# -----------------------------
# GET ALL PRODUCTS FOR USERS
# -----------------------------
@router.get("/", response_model=List[schemas.ProductViewNormalUser], tags=["Product - User APIs"])
async def get_product(
    db: AsyncSession = Depends(get_db), 
    limit: int = 10, 
    skip: int = 0, 
    min_price: int = 0,
    max_price: Optional[int] = None, 
    sort_by: Optional[str] = "id", 
    category: Optional[str] = None
):
    """
    Retrieve a list of products visible to users with support for:
    - pagination (limit, skip)
    - filtering by price range and category
    - sorting by price, stock, or created_at (defaults to ID)
    """
    try:
        # Base query to select all products
        statement = select(models.Product)

        # Apply dynamic filters
        filters = [ models.Product.is_active == True, models.Product.price >= min_price]

        if max_price is not None:
            filters.append(models.Product.price <= max_price)
        
        if category:
            filters.append(models.Product.category == category)

        if filters:
            statement = statement.where(and_(*filters))

        # Apply sorting
        if sort_by in ["price", "stock", "created_at"]:
            statement = statement.order_by(asc(getattr(models.Product, sort_by)))
        else:
            statement = statement.order_by(models.Product.id)

        # Apply pagination
        statement = statement.limit(limit).offset(skip)

        # Execute and fetch results
        result = await db.execute(statement)
        return result.scalars().all()

    except Exception as e:
        logger.error(f"Error retrieving product list: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching product list")


# -----------------------------
# SEARCH PRODUCTS BY NAME
# -----------------------------
@router.get("/search", response_model=List[schemas.ProductViewNormalUser], tags=["Product - User APIs"])
async def product_search(
    db: AsyncSession = Depends(get_db), 
    product_name: Optional[str] = None
):
    """
    Search products by name keyword (case-insensitive).
    """
    try:
        statement = select(models.Product).where(models.Product.is_active == True)

        if product_name:
            statement = statement.where(models.Product.name.ilike(f"%{product_name}%"))

        result = await db.execute(statement)
        return result.scalars().all()

    except Exception as e:
        logger.error(f"Product search failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during product search")


# -----------------------------
# GET PRODUCT DETAILS BY ID
# -----------------------------
@router.get("/{id}", response_model=schemas.ProductViewNormalUserDetailed, tags=["Product - User APIs"])
async def product_by_id(
    id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve detailed product info by its unique ID.
    """
    try:
        statement = select(models.Product).where(models.Product.id == id, models.Product.is_active == True)
        result = await db.execute(statement)
        product = result.scalar_one_or_none()

        if product is None:
            raise ProductNotFoundException(f"Product not found with ID: {id}")

        return product

    except ProductNotFoundException as not_found:
        logger.warning(str(not_found))
        raise not_found

    except Exception as e:
        logger.error(f"Failed to retrieve product with ID {id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching product details")
