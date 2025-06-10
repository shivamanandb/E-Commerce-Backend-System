from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from ..configuration.database import get_db
from . import models as cartModel
from ..middlewares import oauth2
from ..auth import models as userModel
from ..products import models as productModel
from ..exceptions import UserNotFoundException, ProductNotFoundException, InvalidStockException
from ..orders import models as ordersModel
from ..orderItems import models as orderItemsModel
from . import schemas

router = APIRouter()


@router.post("/")
async def add_to_cart(
    cart: schemas.CartData, 
    db: AsyncSession = Depends(get_db), 
    current_user: userModel.User = Depends(oauth2.get_current_user)
):
    # Fetch the product
    product_result = await db.execute(
        select(productModel.Product).where(productModel.Product.id == cart.product_id)
    )
    product = product_result.scalar_one_or_none()

    if product is None:
        raise ProductNotFoundException("Product not found")

    # Check stock
    if product.stock < cart.quantity:
        raise ProductNotFoundException("Only few items available in stock")

    # Check if item is already in cart
    statement = select(cartModel.Cart).where(
        cartModel.Cart.product_id == cart.product_id,
        cartModel.Cart.user_id == current_user.id
    )
    result = await db.execute(statement)
    cart_item = result.scalar_one_or_none()

    if cart_item is None:
        # Add new cart item
        cart_data = cartModel.Cart(
            user_id=current_user.id,
            product_id=cart.product_id,
            quantity=cart.quantity
        )
        db.add(cart_data)
    else:
        # Update existing quantity
        new_quantity = cart_item.quantity + cart.quantity

        if product.stock < new_quantity:
            raise ProductNotFoundException(f"Only few items available in stock. Cannot add {new_quantity} items")

        await db.execute(
            update(cartModel.Cart)
            .where(cartModel.Cart.id == cart_item.id)
            .values(quantity=new_quantity)
        )

    await db.commit()
    return {"message": "Product added to cart and stock updated successfully"}

@router.get("/", response_model=schemas.CartResponse)
async def view_cart(
    db: AsyncSession = Depends(get_db),
    current_user: userModel.User = Depends(oauth2.get_current_user)
):
    result = await db.execute(
        select(cartModel.Cart).where(cartModel.Cart.user_id == current_user.id).options(
            selectinload(cartModel.Cart.product)
        )
    )
    cart_items = result.scalars().all()

    items = []
    total = 0

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

@router.delete("/{product_id}")
async def remove_from_cart(product_id: int, 
                        db: AsyncSession = Depends(get_db),
                        current_user: userModel.User = Depends(oauth2.get_current_user)
                        ):
    
    try:
        
        statement = select(cartModel.Cart).where(
            cartModel.Cart.product_id == product_id,
            cartModel.Cart.user_id == current_user.id
        )
        
        product = await db.execute(statement)
        
        product = product.scalar_one_or_none()
        
        if product is None:
            raise ProductNotFoundException("Product not found")
        
        await db.execute(delete(cartModel.Cart).where(cartModel.Cart.product_id == product_id))
        
        await db.commit()
        
        return {"message": "Product successfully removed from the Cart"}
    except Exception as e:
        raise e

@router.put("/{product_id}")
async def update_quantity(
    product_id: int, 
    productData: schemas.ProductQuantity,
    db: AsyncSession = Depends(get_db),
    current_user: userModel.User = Depends(oauth2.get_current_user)
):
    try:
        statement = select(cartModel.Cart).where(
            cartModel.Cart.product_id == product_id,
            cartModel.Cart.user_id == current_user.id
        ).options(selectinload(cartModel.Cart.product))
        
        cartItem = await db.execute(statement)
        
        cartItem = cartItem.scalar_one_or_none()
        
        if cartItem is None:
            raise ProductNotFoundException("Product not found")

        print(type(cartItem.product.stock))
        # Check stock
        if cartItem.product.stock < productData.quantity:
            raise ProductNotFoundException("Can't add this much quantity. Only few items available in stock")
        
        await db.execute(
            update(cartModel.Cart)
            .where(cartModel.Cart.product_id == product_id)
            .values(quantity=productData.quantity)
        )
        await db.commit()
        
        return {"message": f"Quantity updated successfully for product id: {product_id}"} 
        
    except Exception as e:
        raise
    
@router.post("/checkout")
async def checkout(
    checkOutAddress: schemas.CheckOutAddress,
    db: AsyncSession = Depends(get_db),
    current_user: userModel.User = Depends(oauth2.get_current_user)
):
    try:
        
        statement = select(cartModel.Cart).where(cartModel.Cart.user_id == current_user.id).options(selectinload(cartModel.Cart.product))
        cart = await db.execute(statement)
        cart = cart.scalars().all()
        
        if len(cart) == 0:
            raise ProductNotFoundException("Cart is empty")
        
        # dummy checkout
        
        # check the required quantity of orders present in stock or not
        for item in cart:
            # stock of Products
            update_stock = item.product.stock - item.quantity
            
            if(update_stock < 0):
                raise InvalidStockException("Stock can't be less than ordered Quantity")
        
        
        total_amt = 0
        for items in cart:
            total_amt += items.product.price 
        
        # create order
        order = ordersModel.Order(
            user_id = current_user.id,
            total_amount = total_amt,
            address = checkOutAddress.address,
            status = "paid"
        )
        
        db.add(order)
        await db.commit()
        await db.refresh(order)
        
        # put details of individual product and order details into orderItems table
        for item in cart:
            orderItems = orderItemsModel.OrderItems(
                order_id = order.id,
                product_id = item.product_id,
                quantity = item.quantity,
                price_at_purchase = item.product.price 
            )
            
            db.add(orderItems)
            await db.commit()
            
        # update stock of product
        for item in cart:
            await db.execute(update(productModel.Product).where(productModel.Product.id == item.product_id).values(stock=item.product.stock - item.quantity))
            await db.commit()
            
        # remove items from cart
        for item in cart:
            await db.execute(delete(cartModel.Cart).where(cartModel.Cart.user_id == current_user.id))
            await db.commit()
        
        return {"message": "Checkout successfully !!"}
        
    except Exception as e:
        raise
        