import pytest
from app.core.mt5_manager import ConnectionState, mt5_manager


@pytest.mark.asyncio
async def test_health_endpoint_connected(client):
    mt5_manager.state = ConnectionState.CONNECTED
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["mt5"]["is_connected"] is True
    assert data["mt5"]["state"] == "CONNECTED"


@pytest.mark.asyncio
async def test_health_endpoint_degraded(client):
    mt5_manager.state = ConnectionState.RECONNECTING
    mt5_manager.reconnect_attempts = 3
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["mt5"]["is_connected"] is False
    assert data["mt5"]["state"] == "RECONNECTING"
    assert data["mt5"]["reconnect_attempts"] == 3


@pytest.mark.asyncio
async def test_503_service_unavailable_when_disconnected(client):
    mt5_manager.state = ConnectionState.DISCONNECTED
    mt5_manager.last_error = "MetaTrader 5 connection lost"

    # Any protected endpoint should return 503
    response = await client.get("/api/v1/account")
    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["error"] == "MT5_SERVICE_UNAVAILABLE"
    assert detail["state"] == "DISCONNECTED"


@pytest.mark.asyncio
async def test_503_service_unavailable_when_reconnecting(client):
    mt5_manager.state = ConnectionState.RECONNECTING
    mt5_manager.reconnect_attempts = 2

    # Any protected endpoint should return 503
    response = await client.get("/api/v1/terminal/version")
    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["error"] == "MT5_SERVICE_UNAVAILABLE"
    assert detail["state"] == "RECONNECTING"
