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
            query = query.filter(user_id=current_user.id) # Changed from username to user_id
            filters.append(f"user_id={current_user.id}")

        if params.items_received_status and params.items_received_status != 'all':
            if params.items_received_status in ["0", "1"]:
                query = query.filter(items_received=int(params.items_received_status))
                filters.append(f"items_received={params.items_received_status}")

        if params.search:
            search_query = Q(
                Q(order_no__icontains=params.search),
                Q(tracking_no__icontains=params.search),
                Q(item_name__icontains=params.search),
                # Removed username from search as it's now a foreign key
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
        # Prefetch user data for displaying in the list
        results = await query.offset((params.page - 1) * params.page_size).limit(params.page_size).prefetch_related("user")
        
        logger.info(f"查询返回结果数量: {len(results)}")
        return OrderList(page=params.page, page_size=params.page_size, total=total, data=results)

    async def create_order(self, order: OrderCreate) -> Order:
        logger.info(f"Attempting to create order with data: {order.model_dump()}")
        try:
            # OrderCreate schema now has user_id, which will be passed to the model's user_id field.
            order_data = order.model_dump()
            # Ensure user_id is present, as it's required by the model's ForeignKeyField
            if 'user_id' not in order_data or order_data['user_id'] is None:
                raise HTTPException(status_code=400, detail="user_id is required to create an order.")
            
            # Verify the user exists before creating the order
            try:
                await User.get(id=order_data['user_id'])
            except DoesNotExist:
                raise HTTPException(status_code=400, detail=f"User with id {order_data['user_id']} not found.")

            db_order = await self.model.create(**order_data)
            await db_order.fetch_related("user") # Fetch user to include in the response
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
            db_order = await self.get(id=order_id) # This should already fetch related user if schema expects it
            if not db_order:
                 raise HTTPException(status_code=404, detail="Order not found")
            
            update_data = order_update.model_dump(exclude_unset=True)
            
            # If user_id is being updated, verify the new user exists
            if 'user_id' in update_data and update_data['user_id'] is not None:
                try:
                    await User.get(id=update_data['user_id'])
                except DoesNotExist:
                    raise HTTPException(status_code=400, detail=f"User with id {update_data['user_id']} not found for update.")

            for key, value in update_data.items():
                setattr(db_order, key, value)
            await db_order.save()
            await db_order.fetch_related("user") # Fetch user to include in the response
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
