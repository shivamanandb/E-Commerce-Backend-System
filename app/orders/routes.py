from fastapi import APIRouter, Depends, status
from ..configuration.database import get_db
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from ..auth import models as userModel
from ..middlewares import oauth2 
from ..orders.models import Order
from ..products.models import Product
from ..orders.models import OrderItems
from ..exceptions import GeneralException, OrderNotFoundException

router = APIRouter()

@router.get("/")
async def view_order_history(
    db: AsyncSession = Depends(get_db),
    current_user: userModel.User = Depends(oauth2.get_current_user)
):
    try:
        result = await db.execute(
            select(Order)
            .where(Order.user_id == current_user.id)
            .order_by(Order.created_at.desc())
        )
        orders = result.scalars().all()

        order_history = [
            {
                "order_id": order.id,
                "date": order.created_at,
                "total": float(order.total_amount),
                "status": order.status.value
            }
            for order in orders
        ]

        return {"orders": order_history}
    
    except Exception as e:
        raise GeneralException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch order history: {str(e)}")


@router.get("/{order_id}")
async def view_order_details(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: userModel.User = Depends(oauth2.get_current_user)
):
    try:
        result = await db.execute(
            select(Order)
            .where(Order.id == order_id, Order.user_id == current_user.id)
            .options(selectinload(Order.order_items).selectinload(OrderItems.product))
        )
        order = result.scalar_one_or_none()

        if not order:
            raise OrderNotFoundException("Order not found")

        item_details = []
        for item in order.order_items:
            product = item.product
            if product:
                subtotal = float(item.price_at_purchase) * item.quantity
                item_details.append({
                    "product_name": product.name,
                    "image_url": product.image_url,
                    "quantity": item.quantity,
                    "price_at_purchase": float(item.price_at_purchase),
                    "subtotal": subtotal
                })

        return {
            "order_id": order.id,
            "date": order.created_at,
            "status": order.status.value,
            "total": float(order.total_amount),
            "items": item_details
        }

    except Exception as e:
        raise GeneralException(status_code=500, detail=f"Failed to fetch order details: {str(e)}")
