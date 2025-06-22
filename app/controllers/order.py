from typing import List, Optional
import logging

from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.expressions import Q

from app.models.orders import Order
from app.schemas.orders import OrderCreate, OrderUpdate, OrderQuerySchema, OrderList
from app.models.admin import User
from app.core.crud import CRUDBase

logger = logging.getLogger(__name__)


class OrderController(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def __init__(self):
        super().__init__(model=Order)

    def _apply_order_filters(
        self,
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

        if params.search:
            search_query = Q(
                Q(order_no__icontains=params.search),
                Q(tracking_no__icontains=params.search),
                Q(item_name__icontains=params.search),
                Q(username__icontains=params.search),
                join_type="OR"
            )
            query = query.filter(search_query)
            filters.append(f"search='{params.search}'")

        logger.info(f"构建的查询条件: {', '.join(filters) if filters else '无过滤条件'}")
        return query

    async def get_all(self, params: OrderQuerySchema, current_user: Optional[User] = None) -> OrderList:
        logger.info(f"接收到订单查询请求 - user: {current_user.username if current_user else 'N/A'}, params: {params.model_dump()}")
        query = self.model.all()
        if current_user:
            query = self._apply_order_filters(query, current_user, params)

        query = query.order_by('-created_at')
        total = await query.count()
        results = await query.offset((params.page - 1) * params.page_size).limit(params.page_size)
        
        logger.info(f"查询返回结果数量: {len(results)}")
        return OrderList(page=params.page, page_size=params.page_size, total=total, data=results)

    async def create_order(self, order: OrderCreate) -> Order:
        logger.info(f"Attempting to create order with data: {order.model_dump()}")
        try:
            db_order = await self.model.create(**order.model_dump())
            logger.info(f"Order created successfully: ID {db_order.id}")
            return db_order
        except IntegrityError as e:
            logger.error(f"IntegrityError during order creation: {e}", exc_info=True)
            error_detail = str(e).lower()
            if "unique constraint failed: orders.order_no" in error_detail or "order with this order_no already exists" in error_detail:
                raise HTTPException(status_code=400, detail="Order with this order_no already exists.")
            elif "not null constraint failed" in error_detail:
                failed_field = "unknown"
                try:
                    parts = error_detail.split("not null constraint failed:")
                    if len(parts) > 1:
                        field_info = parts[1].strip()
                        field_parts = field_info.split('.')
                        if field_parts:
                            failed_field = field_parts[-1]
                        else:
                            failed_field = field_info
                except Exception:
                    logger.warning(f"Could not parse field name from error: {error_detail}")
                raise HTTPException(status_code=400, detail=f"Field '{failed_field}' cannot be null.")
            else:
                raise HTTPException(status_code=400, detail=f"Database integrity error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during order creation: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="An unexpected error occurred during order creation.")

    async def update_order(self, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
        try:
            db_order = await self.get(id=order_id)
            if not db_order:
                 raise HTTPException(status_code=404, detail="Order not found")
            update_data = order_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_order, key, value)
            await db_order.save()
            return db_order
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Order not found")

    async def remove_order(self, order_id: int) -> dict:
        try:
            db_order = await self.get(id=order_id)
            if not db_order:
                raise HTTPException(status_code=404, detail="Order not found")
            await db_order.delete()
            return {"message": "Order deleted successfully"}
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Order not found")


order_controller = OrderController()