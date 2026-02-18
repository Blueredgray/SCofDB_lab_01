import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from .exceptions import (
    OrderAlreadyPaidError, 
    OrderCancelledError, 
    InvalidQuantityError, 
    InvalidPriceError
)

class OrderStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    CANCELLED = "cancelled"
    SHIPPED = "shipped"
    COMPLETED = "completed"

@dataclass
class OrderItem:
    product_name: str
    price: Decimal
    quantity: int
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    order_id: Optional[uuid.UUID] = None

    def __post_init__(self):
        if self.price < 0:
            raise InvalidPriceError(self.price)
        if self.quantity <= 0:
            raise InvalidQuantityError(self.quantity)

    @property
    def subtotal(self) -> Decimal:
        return self.price * self.quantity

@dataclass
class OrderStatusChange:
    status: OrderStatus
    changed_at: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)

@dataclass
class Order:
    user_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: OrderStatus = OrderStatus.CREATED
    items: List[OrderItem] = field(default_factory=list)
    total_amount: Decimal = Decimal("0.00")
    created_at: datetime = field(default_factory=datetime.now)
    status_history: List[OrderStatusChange] = field(default_factory=list)

    def add_item(self, product_name: str, price: Decimal, quantity: int) -> OrderItem:
        if self.status == OrderStatus.CANCELLED:
            raise OrderCancelledError(self.id)
        item = OrderItem(product_name=product_name, price=price, quantity=quantity, order_id=self.id)
        self.items.append(item)
        self._recalculate_total()
        return item

    def _recalculate_total(self):
        self.total_amount = sum(item.subtotal for item in self.items)

    def pay(self):
        """КРИТИЧЕСКИЙ МЕТОД"""
        if self.status == OrderStatus.PAID:
            raise OrderAlreadyPaidError(self.id)
        if self.status == OrderStatus.CANCELLED:
            raise OrderCancelledError(self.id)
        self.status = OrderStatus.PAID

    def cancel(self):
        # ИСПРАВЛЕНО: Запрет отмены оплаченного заказа
        if self.status == OrderStatus.PAID:
             raise OrderAlreadyPaidError(self.id)
        if self.status == OrderStatus.SHIPPED or self.status == OrderStatus.COMPLETED:
            raise ValueError(f"Cannot cancel order in status {self.status.name}")
        self.status = OrderStatus.CANCELLED

    def ship(self):
        if self.status != OrderStatus.PAID:
            raise ValueError("Order must be paid before shipping")
        self.status = OrderStatus.SHIPPED

    def complete(self):
        if self.status != OrderStatus.SHIPPED:
            raise ValueError("Order must be shipped before completion")
        self.status = OrderStatus.COMPLETED