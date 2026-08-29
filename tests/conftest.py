import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.mt5_manager import mt5_manager, ConnectionState


@pytest.fixture(autouse=True)
def reset_mt5_state():
    """Ensure MT5 manager state is set to CONNECTED by default for endpoint tests."""
    mt5_manager.state = ConnectionState.CONNECTED
    mt5_manager.last_error = None
    mt5_manager.reconnect_attempts = 0
    yield
    mt5_manager.state = ConnectionState.DISCONNECTED


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
