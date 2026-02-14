"""
Integration tests for API endpoints.

These tests verify that the full stack works correctly.
They require a running database.

To run: pytest app/tests/test_integration.py -v
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


class TestHealthEndpoint:
    """Test that the app starts correctly."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """GET /health should return ok."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}


class TestAPIEndpointsExist:
    """Test that all required endpoints exist."""

    @pytest.mark.asyncio
    async def test_users_endpoint_exists(self):
        """POST /api/users should exist."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/users",
                json={"email": "test@example.com", "name": "Test"}
            )
            # Should not be 404 (endpoint exists)
            # Will be 500 if not implemented, 201 if working
            assert response.status_code != 404

    @pytest.mark.asyncio
    async def test_orders_endpoint_exists(self):
        """POST /api/orders should exist."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/orders",
                json={"user_id": "00000000-0000-0000-0000-000000000000"}
            )
            assert response.status_code != 404

    @pytest.mark.asyncio
    async def test_pay_endpoint_exists(self):
        """POST /api/orders/{id}/pay should exist."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/orders/00000000-0000-0000-0000-000000000000/pay"
            )
            assert response.status_code != 404

    @pytest.mark.asyncio
    async def test_cancel_endpoint_exists(self):
        """POST /api/orders/{id}/cancel should exist."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/orders/00000000-0000-0000-0000-000000000000/cancel"
            )
            assert response.status_code != 404
