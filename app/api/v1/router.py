from fastapi import APIRouter
from app.api.v1 import (
    account,
    health,
    history,
    market_book,
    orders,
    positions,
    rates,
    symbols,
    terminal,
    ticks,
)

api_router = APIRouter(prefix="/api/v1")

# Register health check endpoint (non-protected)
api_router.include_router(health.router)

# Register all MT5-protected endpoints
api_router.include_router(terminal.router)
api_router.include_router(account.router)
api_router.include_router(symbols.router)
api_router.include_router(market_book.router)
api_router.include_router(rates.router)
api_router.include_router(ticks.router)
api_router.include_router(orders.router)
api_router.include_router(positions.router)
api_router.include_router(history.router)
