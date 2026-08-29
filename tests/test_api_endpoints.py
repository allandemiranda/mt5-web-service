from unittest.mock import patch
import pytest
from app.core.constants import MT5Timeframe
from app.core.mt5_manager import ConnectionState, mt5_manager


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data
    assert data["health"] == "/api/v1/health"


@pytest.mark.asyncio
async def test_symbols_total_endpoint(client):
    mt5_manager.state = ConnectionState.CONNECTED
    with patch("app.services.mt5_service.mt5_service.get_symbols_total", return_value=125):
        response = await client.get("/api/v1/symbols/total")
        assert response.status_code == 200
        assert response.json() == 125


@pytest.mark.asyncio
async def test_order_calc_margin(client):
    mt5_manager.state = ConnectionState.CONNECTED
    with patch("app.services.mt5_service.mt5_service.order_calc_margin", return_value=100.0):
        response = await client.post(
            "/api/v1/orders/calc-margin",
            json={
                "action": 0,
                "symbol": "EURUSD",
                "volume": 1.0,
                "price": 1.0850,
            },
        )
        assert response.status_code == 200
        assert response.json() == 100.0


@pytest.mark.asyncio
async def test_rates_from_endpoint(client):
    mt5_manager.state = ConnectionState.CONNECTED
    mock_rates = [
        {
            "time": 1700000000,
            "time_iso": "2023-11-14T22:13:20+00:00",
            "open": 1.0850,
            "high": 1.0870,
            "low": 1.0840,
            "close": 1.0865,
            "tick_volume": 1500,
            "spread": 1,
            "real_volume": 0,
        }
    ]
    with patch("app.services.mt5_service.mt5_service.copy_rates_from", return_value=mock_rates):
        response = await client.get(
            "/api/v1/rates/from",
            params={
                "symbol": "EURUSD",
                "timeframe": "TIMEFRAME_H1",
                "date_from": "2023-11-14T00:00:00",
                "count": 1,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["open"] == 1.0850
