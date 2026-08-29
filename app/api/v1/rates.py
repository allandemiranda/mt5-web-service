from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, Query
from app.api.dependencies import require_mt5_connection
from app.core.constants import MT5Timeframe
from app.schemas.rates import RateBar
from app.services.mt5_service import mt5_service

router = APIRouter(prefix="/rates", tags=["Rates (OHLCV)"], dependencies=[Depends(require_mt5_connection)])


@router.get("/from", response_model=List[RateBar], summary="Get Bars Starting from a Given Date")
async def get_rates_from(
    symbol: str = Query(..., description="Symbol name (e.g. 'EURUSD')"),
    timeframe: MT5Timeframe = Query(MT5Timeframe.TIMEFRAME_H1, description="Chart timeframe"),
    date_from: datetime = Query(..., description="Start date (ISO 8601)"),
    count: int = Query(100, ge=1, le=50000, description="Number of bars to fetch"),
):
    return await mt5_service.copy_rates_from(symbol, timeframe, date_from, count)


@router.get("/from-pos", response_model=List[RateBar], summary="Get Bars Starting from an Index")
async def get_rates_from_pos(
    symbol: str = Query(..., description="Symbol name (e.g. 'EURUSD')"),
    timeframe: MT5Timeframe = Query(MT5Timeframe.TIMEFRAME_H1, description="Chart timeframe"),
    start_pos: int = Query(0, ge=0, description="Start bar index (0 = current bar)"),
    count: int = Query(100, ge=1, le=50000, description="Number of bars to fetch"),
):
    return await mt5_service.copy_rates_from_pos(symbol, timeframe, start_pos, count)


@router.get("/range", response_model=List[RateBar], summary="Get Bars for a Specified Date Range")
async def get_rates_range(
    symbol: str = Query(..., description="Symbol name (e.g. 'EURUSD')"),
    timeframe: MT5Timeframe = Query(MT5Timeframe.TIMEFRAME_H1, description="Chart timeframe"),
    date_from: datetime = Query(..., description="Start date (ISO 8601)"),
    date_to: datetime = Query(..., description="End date (ISO 8601)"),
):
    return await mt5_service.copy_rates_range(symbol, timeframe, date_from, date_to)
