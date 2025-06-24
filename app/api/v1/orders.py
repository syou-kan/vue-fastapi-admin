from typing import List, Optional, Annotated
from tortoise.exceptions import DoesNotExist # Added import
from fastapi import APIRouter, Depends, HTTPException
 
from app.schemas.orders import Order, OrderCreate, OrderUpdate, OrderList, OrderQuerySchema, OrderUpdateByUser
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
    - **item_amount**: Item amount (optional, non-negative float, default 0)
    - **remarks**: Remarks for the order (optional, max 200 chars)
    
    普通用户创建的订单会自动关联到当前用户。
    """
    current_user_id = CTX_USER_ID.get()
    current_user = await User.get(id=current_user_id)
    
    # 确保 OrderCreate 中的 user_id 是有效的
    try:
        await User.get(id=order_in.user_id)
    except DoesNotExist: # Ensure DoesNotExist is imported from tortoise.exceptions
        raise HTTPException(status_code=400, detail=f"User with id {order_in.user_id} not found.")
    
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
    
    await db_order.fetch_related("user") # 确保用户信息被加载

    # 普通用户只能查看自己的订单
    # 注意：db_order 现在通过 prefetch_related 应该有 user 对象，或者直接访问 user_id
    # 我们在 controller 中处理了 prefetch，所以这里可以直接用 db_order.user.id 或 db_order.user_id
    # 为保持一致性，我们假设 controller 返回的 db_order 已经加载了 user 信息或有 user_id
    # 如果 Order 模型中是 user_id 字段，则用 db_order.user_id
    # 如果 Order 模型中是 user 外键，并且已 prefetch，则用 db_order.user.id
    # 根据我们对 Order 模型的修改，它现在是 user 外键，其id字段是 user_id
    if not current_user.is_superuser and db_order.user_id != current_user.id:
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
    - **item_amount**
    - **remarks**
    - **items_received**
    
    普通用户只能更新自己的订单，管理员可以更新任何订单。
    """
    current_user_id = CTX_USER_ID.get()
    current_user = await User.get(id=current_user_id)

    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only administrators can perform this action")
    
    # 首先检查订单是否存在
    db_order = await crud_order.get(id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    updated_order = await crud_order.update_order(order_id=order_id, order_update=order_in)
    if updated_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order


@router.patch("/{item_id}/receipt", response_model=Order, summary="用户确认收货")
async def user_confirm_receipt(
    item_id: int,
    order_in: OrderUpdateByUser,
    current_user: User = DependAuth,
):
    """
    用户确认收货
    """
    db_order = await crud_order.get(id=item_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    if db_order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")

    return await crud_order.update_order(
        order_id=item_id,
        order_update=OrderUpdate(items_received=order_in.is_received),
    )


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
