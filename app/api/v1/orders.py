from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.orders import Order, OrderCreate, OrderUpdate, OrderList, OrderQuerySchema
from app.controllers.order import order_controller as crud_order
from app.models.admin import User
from app.core.dependency import DependAuth, DependPermisson, DependOrderDataIsolation, DependEnhancedPermission
from app.core.ctx import CTX_USER_ID

router = APIRouter(tags=["订单管理"])


@router.post("/", response_model=Order, summary="创建新订单", dependencies=[DependEnhancedPermission])
async def create_order_endpoint(
    order_in: OrderCreate,
):
    """
    Create a new order with the following information:
    - **order_no**: Unique order number (required)
    - **tracking_no**: Tracking number (optional)
    - **item_name**: Name of the item (required)
    - **item_quantity**: Quantity of the item (required, positive integer)
    - **shipping_fee**: Shipping fee (optional, non-negative float, default 0)
    - **remarks**: Remarks for the order (optional, max 200 chars)
    
    普通用户创建的订单会自动关联到当前用户。
    """
    current_user_id = CTX_USER_ID.get()
    current_user = await User.get(id=current_user_id)
    
    # 为普通用户自动设置用户名
    if not current_user.is_superuser:
        order_in.username = current_user.username
    
    return await crud_order.create_order(order=order_in)


@router.get("/", response_model=OrderList, summary="查看订单列表", dependencies=[DependEnhancedPermission])
async def get_orders_endpoint(
    params: OrderQuerySchema = Depends(),
):
    """
    Retrieve a list of orders. Supports pagination and filtering.
    - **page**: Page number
    - **page_size**: Number of items per page
    - **items_received_status**: Filter by items received status ('all', '0', '1')
    
    普通用户只能查看自己的订单，管理员可以查看所有订单。
    """
    current_user_id = CTX_USER_ID.get()
    current_user = await User.get(id=current_user_id)
    
    return await crud_order.get_all(params=params, current_user=current_user)


@router.get("/{order_id}", response_model=Order, summary="获取指定ID的订单", dependencies=[DependEnhancedPermission])
async def get_order_endpoint(
    order_id: int,
):
    """
    Get details of a specific order by its ID.
    普通用户只能查看自己的订单，管理员可以查看任何订单。
    """
    current_user_id = CTX_USER_ID.get()
    current_user = await User.get(id=current_user_id)
    
    db_order = await crud_order.get(id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 普通用户只能查看自己的订单
    if not current_user.is_superuser and db_order.username != current_user.username:
        raise HTTPException(
            status_code=403, 
            detail="Access denied: You can only view your own orders"
        )
    
    return db_order


@router.put("/{order_id}", response_model=Order, summary="更新订单", dependencies=[DependEnhancedPermission])
async def update_order_endpoint(
    order_id: int,
    order_in: OrderUpdate,
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
    
    普通用户只能更新自己的订单，管理员可以更新任何订单。
    """
    current_user_id = CTX_USER_ID.get()
    current_user = await User.get(id=current_user_id)
    
    # 首先检查订单是否存在
    db_order = await crud_order.get(id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 普通用户只能更新自己的订单
    if not current_user.is_superuser and db_order.username != current_user.username:
        raise HTTPException(
            status_code=403, 
            detail="Access denied: You can only update your own orders"
        )
    
    # 普通用户不能修改订单的用户名
    if not current_user.is_superuser:
        update_data = order_in.model_dump(exclude_unset=True)
        if 'username' in update_data and update_data['username'] != current_user.username:
            raise HTTPException(
                status_code=403,
                detail="Access denied: You cannot change the order owner"
            )
    
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
    注意：删除订单功能通常只对管理员开放，普通用户不应该有删除权限。
    """
    current_user_id = CTX_USER_ID.get()
    current_user = await User.get(id=current_user_id)
    
    # 检查订单是否存在
    db_order = await crud_order.get(id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 普通用户不能删除订单（根据权限设计，普通用户没有DELETE权限）
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Regular users cannot delete orders"
        )
    
    result = await crud_order.remove_order(order_id=order_id)
    if result.get("message") != "Order deleted successfully":
        raise HTTPException(status_code=404, detail="Order not found or could not be deleted")
    return result
