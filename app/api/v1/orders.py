from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.orders import Order, OrderCreate, OrderUpdate, OrderList
from app.controllers import order as crud_order
from app.models.admin import User # Added import
from app.core.dependency import DependAuth # Added import

router = APIRouter()

@router.post("/", response_model=Order, summary="Create a new order", tags=["orders"])
async def create_order_endpoint(
    order_in: OrderCreate,
    # current_user: User = Depends(check_permission) # Example permission, adapt as needed
):
    """
    Create a new order with the following information:
    - **order_no**: Unique order number (required)
    - **tracking_no**: Tracking number (optional)
    - **item_name**: Name of the item (required)
    """
    return await crud_order.create_order(order=order_in)


@router.get("/", response_model=OrderList, summary="查看订单", tags=["orders"])
async def get_orders_endpoint(
    current_user: Annotated[User, DependAuth], # Modified
    skip: int = 0,
    limit: int = 10,
    order_no: Optional[str] = None,
    item_name: Optional[str] = None
):
    """
    Retrieve a list of orders. Supports pagination and filtering.
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **order_no**: Filter by order number (partial match)
    - **item_name**: Filter by item name (partial match)
    """
    orders = await crud_order.get_orders(
        skip=skip, limit=limit, order_no=order_no, item_name=item_name, current_user=current_user # Modified
    )
    # Assuming OrderList expects a 'data' field and total count for pagination
    # This might need adjustment based on how BasePagination is defined and how Tortoise handles counts
    total_count = await crud_order.get_orders_count(order_no=order_no, item_name=item_name, current_user=current_user) # Modified
    # Convert list of model objects to list of schema objects
    orders_schema = [Order.from_orm(order_model) for order_model in orders]
    return OrderList(data=orders_schema, total=total_count, page= (skip // limit) + 1, page_size=limit)


@router.get("/{order_id}", response_model=Order, summary="Get a specific order by ID", tags=["orders"])
async def get_order_endpoint(
    order_id: int,
    # current_user: User = Depends(check_permission) # Example permission, adapt as needed
):
    """
    Get details of a specific order by its ID.
    """
    db_order = await crud_order.get_order(order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


@router.put("/{order_id}", response_model=Order, summary="Update an existing order", tags=["orders"])
async def update_order_endpoint(
    order_id: int,
    order_in: OrderUpdate,
    # current_user: User = Depends(check_permission) # Example permission, adapt as needed
):
    """
    Update an existing order. Only provided fields will be updated.
    """
    updated_order = await crud_order.update_order(order_id=order_id, order_update=order_in)
    if updated_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order


@router.delete("/{order_id}", summary="Delete an order", tags=["orders"])
async def delete_order_endpoint(
    order_id: int,
    # current_user: User = Depends(check_permission) # Example permission, adapt as needed
):
    """
    Delete an order by its ID.
    """
    result = await crud_order.remove_order(order_id=order_id)
    if result.get("message") != "Order deleted successfully": # Check message from controller
        raise HTTPException(status_code=404, detail="Order not found or could not be deleted")
    return result