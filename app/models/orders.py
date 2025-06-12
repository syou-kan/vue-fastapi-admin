from tortoise import fields
from tortoise.models import Model
from datetime import datetime

class Order(Model):
    id = fields.IntField(pk=True, index=True, generated=True)
    order_no = fields.CharField(max_length=255, unique=True, index=True, null=False)
    tracking_no = fields.CharField(max_length=255, null=True)
    item_name = fields.CharField(max_length=255, null=False)
    username = fields.CharField(max_length=255, null=False, description="Username")
    items_received = fields.BooleanField(default=False, null=False, description="Whether the items have been received")
    created_at = fields.DatetimeField(auto_now_add=True, description="Creation timestamp")
    updated_at = fields.DatetimeField(auto_now=True, description="Last update timestamp")

    class Meta:
        table = "orders"

    def __str__(self):
        return self.order_no