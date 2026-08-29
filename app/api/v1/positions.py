from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.api.dependencies import require_mt5_connection
from app.schemas.orders import OrderSendResult
from app.schemas.positions import PositionCloseRequest, PositionInfo
from app.services.mt5_service import mt5_service

router = APIRouter(prefix="/positions", tags=["Positions"], dependencies=[Depends(require_mt5_connection)])


@router.get("/total", response_model=int, summary="Get Total Open Positions Count")
async def get_positions_total():
    return await mt5_service.get_positions_total()


@router.get("", response_model=List[PositionInfo], summary="Get Open Positions List")
async def get_positions(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    group: Optional[str] = Query(None, description="Filter by group mask"),
    ticket: Optional[int] = Query(None, description="Filter by position ticket"),
):
    return await mt5_service.get_positions(symbol=symbol, group=group, ticket=ticket)


@router.post("/{ticket}/close", response_model=OrderSendResult, summary="Close Position by Ticket")
async def close_position(ticket: int, req: PositionCloseRequest):
    return await mt5_service.close_position(ticket, deviation=req.deviation, comment=req.comment)
