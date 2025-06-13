from typing import List, Optional
import logging # 新增日志模块导入

from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError

from app.models.orders import Order
from app.schemas.orders import OrderCreate, OrderUpdate, OrderQuerySchema
from app.models.admin import User # Added import

logger = logging.getLogger(__name__) # 获取 logger 实例


async def create_order(order: OrderCreate) -> Order:
    logger.info(f"Attempting to create order with data: {order.model_dump()}")
    try:
        db_order = await Order.create(**order.model_dump())
        logger.info(f"Order created successfully: ID {db_order.id}")
        return db_order
    except IntegrityError as e:
        logger.error(f"IntegrityError during order creation: {e}", exc_info=True)
        error_detail = str(e).lower()
        if "unique constraint failed: orders.order_no" in error_detail or "order with this order_no already exists" in error_detail: # 检查 SQLite 和 PostgreSQL 的常见错误信息
            raise HTTPException(status_code=400, detail="Order with this order_no already exists.")
        elif "not null constraint failed" in error_detail:
            # 尝试从错误信息中提取字段名
            failed_field = "unknown" # Default value
            try:
                parts = error_detail.split("not null constraint failed:")
                if len(parts) > 1:
                    field_info = parts[1].strip() # Get the part after the keyword and strip whitespace
                    field_parts = field_info.split('.') # Split by dot (e.g., table.column)
                    if field_parts:
                        failed_field = field_parts[-1] # Get the last part (column name)
                    else:
                        failed_field = field_info # Fallback if no dot
            except Exception: # Broad exception to catch any parsing errors
                logger.warning(f"Could not parse field name from error: {error_detail}")
            raise HTTPException(status_code=400, detail=f"Field '{failed_field}' cannot be null.")
        else:
            raise HTTPException(status_code=400, detail=f"Database integrity error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during order creation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred during order creation.")


async def get_order(order_id: int) -> Optional[Order]:
    try:
        return await Order.get(id=order_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Order not found")

def _apply_order_filters(
    query,
    current_user: User,
    params: OrderQuerySchema
):
    filters = []
    if current_user and not current_user.is_superuser:
        query = query.filter(username=current_user.username)
        filters.append(f"username={current_user.username}")

    if params.items_received_status in ["0", "1"]:
        query = query.filter(items_received=int(params.items_received_status))
        filters.append(f"items_received={params.items_received_status}")

    # You can add other filters from params here if needed in the future
    # For example:
    # if params.order_no:
    #     query = query.filter(order_no__icontains=params.order_no)
    #     filters.append(f"order_no__icontains={params.order_no}")

    logger.info(f"构建的查询条件: {', '.join(filters) if filters else '无过滤条件'}")
    return query

async def get_orders(
    current_user: User,
    params: OrderQuerySchema,
) -> List[Order]:
    logger.info(f"接收到订单查询请求 - user: {current_user.username}, params: {params.model_dump()}")
    
    query = Order.all()
    query = _apply_order_filters(query, current_user, params)
    
    results = await query.offset((params.page - 1) * params.page_size).limit(params.page_size)
    logger.info(f"查询返回结果数量: {len(results)}")
    
    return results

async def get_orders_count(
    current_user: User,
    params: OrderQuerySchema,
) -> int:
    logger.info(f"获取订单总数 - user: {current_user.username}, params: {params.model_dump()}")
    
    query = Order.all()
    query = _apply_order_filters(query, current_user, params)
    
    count = await query.count()
    logger.info(f"订单总数: {count}")
    
    return count

async def update_order(order_id: int, order_update: OrderUpdate) -> Optional[Order]:
    try:
        db_order = await Order.get(id=order_id)
        update_data = order_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_order, key, value)
        await db_order.save()
        return db_order
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Order not found")


async def remove_order(order_id: int) -> dict:
    try:
        db_order = await Order.get(id=order_id)
        await db_order.delete()
        return {"message": "Order deleted successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Order not found")