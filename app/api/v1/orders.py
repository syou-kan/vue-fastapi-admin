from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.orders import Order, OrderCreate, OrderUpdate, OrderList, OrderQuerySchema
from app.controllers.order import order_controller as crud_order
from app.models.admin import User # Added import
from app.core.dependency import DependAuth, DependPermisson

router = APIRouter(tags=["订单管理"])

@router.post("/", response_model=Order, summary="创建新订单")
async def create_order_endpoint(
    order_in: OrderCreate,
    _: User = DependPermisson,
):
    """
    Create a new order with the following information:
    - **order_no**: Unique order number (required)
    - **tracking_no**: Tracking number (optional)
    - **item_name**: Name of the item (required)
    - **item_quantity**: Quantity of the item (required, positive integer)
    - **shipping_fee**: Shipping fee (optional, non-negative float, default 0)
    - **remarks**: Remarks for the order (optional, max 200 chars)
    """
    return await crud_order.create_order(order=order_in)


@router.get("/", response_model=OrderList, summary="查看所有订单")
async def get_orders_endpoint(
    current_user: Annotated[User, DependAuth],
    params: OrderQuerySchema = Depends(),
):
    """
    Retrieve a list of orders. Supports pagination and filtering.
    - **page**: Page number
    - **page_size**: Number of items per page
    - **items_received_status**: Filter by items received status ('all', '0', '1')
    """
    return await crud_order.get_all(params=params, current_user=current_user)


@router.get("/{order_id}", response_model=Order, summary="获取指定ID的订单")
async def get_order_endpoint(
    order_id: int,
    _: User = DependPermisson,
):
    """
    Get details of a specific order by its ID.
    """
    db_order = await crud_order.get(id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


@router.put("/{order_id}", response_model=Order, summary="更新订单")
async def update_order_endpoint(
    order_id: int,
    order_in: OrderUpdate,
    _: User = DependPermisson,
):
    """
    Update an existing order. Only provided fields will be updated.
    Fields that can be updated:
    - **order_no**
    - **tracking_no**
    - **item_name**
    - **item_quantity**
    - **shipping_fee**
    - **remarks**
    - **items_received**
    """
    updated_order = await crud_order.update_order(order_id=order_id, order_update=order_in)
    if updated_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order


@router.delete("/{order_id}", summary="删除订单")
async def delete_order_endpoint(
    order_id: int,
    _: User = DependPermisson,
):
    """
    Delete an order by its ID.
    """
    result = await crud_order.remove_order(order_id=order_id)
    if result.get("message") != "Order deleted successfully": # Check message from controller
        raise HTTPException(status_code=404, detail="Order not found or could not be deleted")
    return result