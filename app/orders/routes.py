from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..configuration.database import get_db
from ..auth import models as user_model
from ..middlewares import oauth2
from ..orders.models import Order, OrderItems
from ..products.models import Product
from ..exceptions import GeneralException, OrderNotFoundException

router = APIRouter()

# --------------------------------------------------------
# Endpoint: View Order History (GET /orders/)
# --------------------------------------------------------

@router.get("/", status_code=status.HTTP_200_OK)
async def view_order_history(
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(oauth2.get_current_user)
):
    """
    Retrieve a list of all past orders placed by the currently authenticated user.

    Returns:
        List of orders with basic information (id, status, total amount, created date).
    """
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
                "status": order.status.value,
            }
            for order in orders
        ]

        return {"orders": order_history}

    except Exception as e:
        raise GeneralException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch order history: {str(e)}"
        )


# --------------------------------------------------------
# Endpoint: View Order Details (GET /orders/{order_id})
# --------------------------------------------------------

@router.get("/{order_id}", status_code=status.HTTP_200_OK)
async def view_order_details(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: user_model.User = Depends(oauth2.get_current_user)
):
    """
    Retrieve full details of a specific order for the logged-in user.

    Args:
        order_id (int): Unique ID of the order to fetch.

    Returns:
        Order metadata and all order items (product info, quantity, prices, etc).
    """
    try:
        result = await db.execute(
            select(Order)
            .where(Order.id == order_id, Order.user_id == current_user.id)
            .order_by(Order.created_at.desc())
            .options(selectinload(Order.order_items).selectinload(OrderItems.product))
        )

        order = result.scalar_one_or_none()

        if not order:
            raise OrderNotFoundException("Order not found")

        item_details = []
        for item in order.order_items:
            product = item.product
            if product:
                item_details.append({
                    "product_name": product.name,
                    "image_url": product.image_url,
                    "quantity": item.quantity,
                    "price_at_purchase": float(item.price_at_purchase),
                    "subtotal": float(item.price_at_purchase) * item.quantity
                })

        return {
            "order_id": order.id,
            "date": order.created_at,
            "status": order.status.value,
            "total": float(order.total_amount),
            "items": item_details
        }

    except OrderNotFoundException:
        raise

    except Exception as e:
        raise GeneralException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch order details: {str(e)}"
        )
