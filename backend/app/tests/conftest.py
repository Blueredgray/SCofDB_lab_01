"""Pytest configuration and fixtures."""

import asyncio
import pytest
import uuid


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_user_id():
    """Create a sample user ID."""
    return uuid.uuid4()
