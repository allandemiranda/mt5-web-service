from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, Query
from app.api.dependencies import require_mt5_connection
from app.core.constants import MT5CopyTicks
from app.schemas.ticks import TickRecord
from app.services.mt5_service import mt5_service

router = APIRouter(prefix="/ticks", tags=["Ticks Data"], dependencies=[Depends(require_mt5_connection)])


@router.get("/from", response_model=List[TickRecord], summary="Get Ticks Starting from Date")
async def get_ticks_from(
    symbol: str = Query(..., description="Symbol name (e.g. 'EURUSD')"),
    date_from: datetime = Query(..., description="Start date (ISO 8601)"),
    count: int = Query(500, ge=1, le=100000, description="Number of ticks"),
    flags: MT5CopyTicks = Query(MT5CopyTicks.COPY_TICKS_ALL, description="Tick filtering flag"),
):
    return await mt5_service.copy_ticks_from(symbol, date_from, count, flags)


@router.get("/range", response_model=List[TickRecord], summary="Get Ticks in Date Range")
async def get_ticks_range(
    symbol: str = Query(..., description="Symbol name (e.g. 'EURUSD')"),
    date_from: datetime = Query(..., description="Start date (ISO 8601)"),
    date_to: datetime = Query(..., description="End date (ISO 8601)"),
    flags: MT5CopyTicks = Query(MT5CopyTicks.COPY_TICKS_ALL, description="Tick filtering flag"),
):
    return await mt5_service.copy_ticks_range(symbol, date_from, date_to, flags)
