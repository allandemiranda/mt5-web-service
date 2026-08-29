from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.api.dependencies import require_mt5_connection
from app.schemas.orders import (
    CalcMarginRequest,
    CalcProfitRequest,
    OrderCheckResult,
    OrderInfo,
    OrderSendResult,
    TradeRequest,
)
from app.services.mt5_service import mt5_service

router = APIRouter(prefix="/orders", tags=["Orders & Trading"], dependencies=[Depends(require_mt5_connection)])


@router.get("/total", response_model=int, summary="Get Total Active Orders Count")
async def get_orders_total():
    return await mt5_service.get_orders_total()


@router.get("", response_model=List[OrderInfo], summary="Get Active Orders List")
async def get_orders(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    group: Optional[str] = Query(None, description="Filter by group mask"),
    ticket: Optional[int] = Query(None, description="Filter by order ticket"),
):
    return await mt5_service.get_orders(symbol=symbol, group=group, ticket=ticket)


@router.post("/check", response_model=OrderCheckResult, summary="Check and Validate Trade Order")
async def check_order(req: TradeRequest):
    return await mt5_service.order_check(req)


@router.post("/send", response_model=OrderSendResult, summary="Send Trade Order to MetaTrader 5")
async def send_order(req: TradeRequest):
    return await mt5_service.order_send(req)


@router.post("/calc-margin", response_model=float, summary="Calculate Required Margin")
async def calc_margin(req: CalcMarginRequest):
    return await mt5_service.order_calc_margin(req.action.value, req.symbol, req.volume, req.price)


@router.post("/calc-profit", response_model=float, summary="Calculate Expected Trade Profit")
async def calc_profit(req: CalcProfitRequest):
    return await mt5_service.order_calc_profit(req.action.value, req.symbol, req.volume, req.price_open, req.price_close)
