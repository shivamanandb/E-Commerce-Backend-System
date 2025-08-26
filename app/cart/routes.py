from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from configuration.database import get_db
from . import models as cartModel
from middlewares import oauth2
from auth import models as userModel
from products import models as productModel
from orders import models as ordersModel
from orders.models import OrderStatus
from exceptions import (
    UserNotFoundException, 
    ProductNotFoundException, 
    InvalidStockException
)
from . import schemas

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    cart: schemas.CartData, 
    db: AsyncSession = Depends(get_db), 
    current_user: userModel.User = Depends(oauth2.get_current_user)
):
    """
    Add a product to the cart.
    If the product already exists in cart, update its quantity.
    Checks if the requested quantity is available in stock.
    """
    product_result = await db.execute(
        select(productModel.Product).where(productModel.Product.id == cart.product_id)
    )
    product = product_result.scalar_one_or_none()

    if product is None:
        raise ProductNotFoundException("Product not found")

    if product.stock < cart.quantity:
        raise ProductNotFoundException("Can't add this much quantity. Only few items available in stock")

    statement = select(cartModel.Cart).where(
        cartModel.Cart.product_id == cart.product_id,
        cartModel.Cart.user_id == current_user.id
    )
    result = await db.execute(statement)
    cart_item = result.scalar_one_or_none()

    if cart_item is None:
        db.add(cartModel.Cart(
            user_id=current_user.id,
            product_id=cart.product_id,
            quantity=cart.quantity
        ))
    else:
        new_quantity = cart_item.quantity + cart.quantity
        if product.stock < new_quantity:
            raise ProductNotFoundException("Cant add this much Quantity. Only few items available in stock")

        await db.execute(
            update(cartModel.Cart)
            .where(cartModel.Cart.id == cart_item.id)
            .values(quantity=new_quantity)
        )

    await db.commit()
    return {"message": "Product added to cart successfully"}


@router.get("/", response_model=schemas.CartResponse)
async def view_cart(
    db: AsyncSession = Depends(get_db),
    current_user: userModel.User = Depends(oauth2.get_current_user)
):
    """
    Retrieve all items in the user's cart, including product details and total cost.
    """
    result = await db.execute(
        select(cartModel.Cart)
        .where(cartModel.Cart.user_id == current_user.id)
        .options(selectinload(cartModel.Cart.product))
    )
    cart_items = result.scalars().all()

    total = 0
    items = []

    for item in cart_items:
        product = item.product
        subtotal = item.quantity * product.price
        total += subtotal
        items.append(schemas.CartProduct(
            id=product.id,
            name=product.name,
            image_url=product.image_url,
            price=product.price,
            quantity=item.quantity,
            subtotal=subtotal
        ))

    return schemas.CartResponse(items=items, total_amount=total)


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def remove_from_cart(
    product_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: userModel.User = Depends(oauth2.get_current_user)
):
    """
    Remove a specific product from the user's cart.
    """
    statement = select(cartModel.Cart).where(
        cartModel.Cart.product_id == product_id,
        cartModel.Cart.user_id == current_user.id
    )
    result = await db.execute(statement)
    cart_item = result.scalar_one_or_none()

    if cart_item is None:
        raise ProductNotFoundException("Product not found in cart")

    await db.execute(delete(cartModel.Cart).where(cartModel.Cart.id == cart_item.id))
    await db.commit()

    return {"message": "Product successfully removed from the cart"}


@router.put("/{product_id}", status_code=status.HTTP_200_OK)
async def update_quantity(
    product_id: int, 
    productData: schemas.ProductQuantity,
    db: AsyncSession = Depends(get_db),
    current_user: userModel.User = Depends(oauth2.get_current_user)
):
    """
    Update quantity of a product in the user's cart after verifying stock availability.
    """
    result = await db.execute(
        select(cartModel.Cart).where(
            cartModel.Cart.product_id == product_id,
            cartModel.Cart.user_id == current_user.id
        ).options(selectinload(cartModel.Cart.product))
    )
    cartItem = result.scalar_one_or_none()

    if cartItem is None:
        raise ProductNotFoundException("Product not found in cart")

    if cartItem.product.stock < productData.quantity:
        raise ProductNotFoundException("Insufficient stock for requested quantity")

    await db.execute(
        update(cartModel.Cart)
        .where(cartModel.Cart.id == cartItem.id)
        .values(quantity=productData.quantity)
    )
    await db.commit()

    return {"message": f"Quantity updated successfully for product id: {product_id}"}


@router.post("/checkout", status_code=status.HTTP_200_OK)
async def checkout(
    checkOutAddress: schemas.CheckOutAddress,
    db: AsyncSession = Depends(get_db),
    current_user: userModel.User = Depends(oauth2.get_current_user)
):
    """
    Place an order based on items in the cart:
    - Validate stock
    - Create order and order items
    - Update stock
    - Clear cart
    """
    result = await db.execute(
        select(cartModel.Cart)
        .where(cartModel.Cart.user_id == current_user.id)
        .options(selectinload(cartModel.Cart.product))
    )
    cart = result.scalars().all()

    if not cart:
        raise ProductNotFoundException("Cart is empty")

    # Validate stock availability
    for item in cart:
        if item.product.stock < item.quantity:
            raise InvalidStockException(f"Insufficient stock for product ID {item.product_id}")

    # Calculate total amount
    total_amt = sum(item.product.price * item.quantity for item in cart)

    # Create order
    order = ordersModel.Order(
        user_id=current_user.id,
        total_amount=total_amt,
        address=checkOutAddress.address,
        status=OrderStatus.paid
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    # Add order items
    for item in cart:
        db.add(ordersModel.OrderItems(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item.product.price
        ))

    # Update product stock
    for item in cart:
        await db.execute(
            update(productModel.Product)
            .where(productModel.Product.id == item.product_id)
            .values(stock=item.product.stock - item.quantity)
        )

    # Clear user's cart
    await db.execute(
        delete(cartModel.Cart).where(cartModel.Cart.user_id == current_user.id)
    )

    await db.commit()

    return {"message": "Checkout completed successfully"}
