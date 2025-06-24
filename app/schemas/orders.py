from typing import List, Optional, Generic, TypeVar

from app.schemas.users import UserSimpleOut
from pydantic import BaseModel, Field
from datetime import datetime

# Temporary base models to resolve import errors
# TODO: Define these properly based on project structure in app.schemas.base
DataT = TypeVar('DataT')

class CustomBaseModel(BaseModel):
    pass

class BasePagination(BaseModel, Generic[DataT]):
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Page size")
    total: int = Field(0, ge=0, description="Total items")
    data: List[DataT] = Field(..., description="List of items")


class OrderBase(CustomBaseModel):
    order_no: str = Field(..., description="Order number")
    tracking_no: Optional[str] = Field(None, description="Tracking number")
    item_name: str = Field(..., description="Item name")
    item_quantity: int = Field(..., gt=0, description="物品数量")
    item_amount: float = Field(0, ge=0, description="物品金额")
    remarks: Optional[str] = Field(None, max_length=200, description="备注")
    user_id: int = Field(..., description="用户ID")
    items_received: bool = Field(False, description="Whether the items have been received")


class OrderCreate(OrderBase):
    pass


class OrderUpdate(CustomBaseModel):
    order_no: Optional[str] = Field(None, description="Order number")
    tracking_no: Optional[str] = Field(None, description="Tracking number")
    item_name: Optional[str] = Field(None, description="Item name")
    item_quantity: Optional[int] = Field(None, gt=0, description="物品数量")
    item_amount: Optional[float] = Field(None, ge=0, description="物品金额")
    remarks: Optional[str] = Field(None, max_length=200, description="备注")
    user_id: Optional[int] = Field(None, description="用户ID")
    items_received: bool | None = Field(None, description="Whether the items have been received")


class OrderUpdateByUser(CustomBaseModel):
    is_received: bool


class OrderInDBBase(OrderBase):
    id: int = Field(..., description="Order ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    items_received: bool = Field(..., description="Whether the items have been received")
    user: UserSimpleOut = Field(..., description="关联用户信息")

    class Config:
        from_attributes = True


class Order(OrderInDBBase):
    pass


class OrderQuerySchema(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Page size")
    items_received_status: Optional[str] = Field(None, description="Items received status (all, 0, 1)")
    search: Optional[str] = Field(None, description="Search keyword for order_no, tracking_no, or item_name")


class OrderList(BasePagination[Order]): # Use the generic BasePagination
    # The 'data' field is now inherited from BasePagination
    pass