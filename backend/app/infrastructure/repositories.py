"""Реализация репозиториев с использованием SQLAlchemy."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user import User
from app.domain.order import Order, OrderItem, OrderStatus, OrderStatusChange


def _convert_decimal(value):
    """Convert Decimal to float for SQLite compatibility."""
    if isinstance(value, Decimal):
        return float(value)
    return value


class UserRepository:
    """Репозиторий для User."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, user: User) -> User:
        """Save user to database."""
        query = text("""
            INSERT INTO users (id, email, name, created_at)
            VALUES (:id, :email, :name, :created_at)
            ON CONFLICT (id) DO UPDATE 
            SET email = EXCLUDED.email, name = EXCLUDED.name
        """)
        await self.session.execute(query, {
            "id": str(user.id), 
            "email": user.email, 
            "name": user.name, 
            "created_at": user.created_at
        })
        return user

    async def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Find user by ID."""
        query = text("SELECT id, email, name, created_at FROM users WHERE id = :id")
        result = await self.session.execute(query, {"id": str(user_id)})
        row = result.mappings().first()
        if row:
            return User(**row)
        return None

    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        query = text("SELECT id, email, name, created_at FROM users WHERE email = :email")
        result = await self.session.execute(query, {"email": email})
        row = result.mappings().first()
        if row:
            return User(**row)
        return None

    async def find_all(self) -> List[User]:
        """Find all users."""
        query = text("SELECT id, email, name, created_at FROM users")
        result = await self.session.execute(query)
        return [User(**row) for row in result.mappings().all()]


class OrderRepository:
    """Репозиторий для Order."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, order: Order) -> Order:
        """Save order to database."""
        query_order = text("""
            INSERT INTO orders (id, user_id, status_id, total_amount, created_at)
            VALUES (
                :id, 
                :user_id, 
                (SELECT id FROM order_statuses WHERE name = :status), 
                :total_amount, 
                :created_at
            )
            ON CONFLICT (id) DO UPDATE 
            SET status_id = EXCLUDED.status_id,
                total_amount = EXCLUDED.total_amount
        """)
        await self.session.execute(query_order, {
            "id": str(order.id), 
            "user_id": str(order.user_id),
            "status": order.status.value, 
            "total_amount": _convert_decimal(order.total_amount),
            "created_at": order.created_at
        })

        # Delete old items and insert new ones
        await self.session.execute(
            text("DELETE FROM order_items WHERE order_id = :id"), 
            {"id": str(order.id)}
        )
        
        for item in order.items:
            await self.session.execute(text("""
                INSERT INTO order_items (id, order_id, product_name, price, quantity)
                VALUES (:id, :order_id, :product_name, :price, :quantity)
            """), {
                "id": str(item.id), 
                "order_id": str(order.id),
                "product_name": item.product_name, 
                "price": _convert_decimal(item.price),
                "quantity": item.quantity
            })
            
        return order

    async def find_by_id(self, order_id: uuid.UUID) -> Optional[Order]:
        """Find order by ID with all items and history."""
        query = text("""
            SELECT o.id, o.user_id, o.total_amount, o.created_at, s.name as status_name
            FROM orders o
            JOIN order_statuses s ON o.status_id = s.id
            WHERE o.id = :id
        """)
        result = await self.session.execute(query, {"id": str(order_id)})
        row = result.mappings().first()
        if not row:
            return None

        order = object.__new__(Order)
        order.id = row['id']
        order.user_id = row['user_id']
        order.status = OrderStatus(row['status_name'])
        order.total_amount = row['total_amount']
        order.created_at = row['created_at']
        order.items = []
        order.status_history = []

        items_res = await self.session.execute(
            text("SELECT id, product_name, price, quantity FROM order_items WHERE order_id = :id"), 
            {"id": str(order_id)}
        )
        for r in items_res.mappings().all():
            item = OrderItem(
                id=r['id'], 
                product_name=r['product_name'], 
                price=r['price'], 
                quantity=r['quantity'], 
                order_id=order_id
            )
            order.items.append(item)

        hist_res = await self.session.execute(
            text("""
                SELECT h.id, s.name, h.changed_at 
                FROM order_status_history h
                JOIN order_statuses s ON h.status_id = s.id
                WHERE h.order_id = :id ORDER BY h.changed_at
            """), 
            {"id": str(order_id)}
        )
        for r in hist_res.mappings().all():
            change = OrderStatusChange(
                id=r['id'], 
                status=OrderStatus(r['name']), 
                changed_at=r['changed_at']
            )
            order.status_history.append(change)

        return order

    async def find_by_user(self, user_id: uuid.UUID) -> List[Order]:
        """Find all orders for a user."""
        query = text("SELECT id FROM orders WHERE user_id = :user_id")
        result = await self.session.execute(query, {"user_id": str(user_id)})
        rows = result.mappings().all()
        orders = []
        for r in rows:
            order = await self.find_by_id(r['id'])
            if order: 
                orders.append(order)
        return orders

    async def find_all(self) -> List[Order]:
        """Find all orders."""
        query = text("SELECT id FROM orders")
        result = await self.session.execute(query)
        rows = result.mappings().all()
        orders = []
        for r in rows:
            order = await self.find_by_id(r['id'])
            if order: 
                orders.append(order)
        return orders
