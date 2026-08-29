from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.api.dependencies import require_mt5_connection
from app.schemas.history import HistoryDeal
from app.schemas.orders import OrderInfo
from app.services.mt5_service import mt5_service

router = APIRouter(prefix="/history", tags=["Trade History"], dependencies=[Depends(require_mt5_connection)])


@router.get("/orders/total", response_model=int, summary="Get Total Historical Orders Count")
async def get_history_orders_total(
    date_from: datetime = Query(..., description="Start date (ISO 8601)"),
    date_to: datetime = Query(..., description="End date (ISO 8601)"),
):
    return await mt5_service.get_history_orders_total(date_from, date_to)


@router.get("/orders", response_model=List[OrderInfo], summary="Get Historical Orders")
async def get_history_orders(
    date_from: Optional[datetime] = Query(None, description="Start date (ISO 8601)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO 8601)"),
    group: Optional[str] = Query(None, description="Group mask filter"),
    ticket: Optional[int] = Query(None, description="Order ticket"),
    position: Optional[int] = Query(None, description="Position ID"),
):
    return await mt5_service.get_history_orders(date_from, date_to, group=group, ticket=ticket, position=position)


@router.get("/deals/total", response_model=int, summary="Get Total Historical Deals Count")
async def get_history_deals_total(
    date_from: datetime = Query(..., description="Start date (ISO 8601)"),
    date_to: datetime = Query(..., description="End date (ISO 8601)"),
):
    return await mt5_service.get_history_deals_total(date_from, date_to)


@router.get("/deals", response_model=List[HistoryDeal], summary="Get Historical Deals")
async def get_history_deals(
    date_from: Optional[datetime] = Query(None, description="Start date (ISO 8601)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO 8601)"),
    group: Optional[str] = Query(None, description="Group mask filter"),
    ticket: Optional[int] = Query(None, description="Deal ticket"),
    position: Optional[int] = Query(None, description="Position ID"),
):
    return await mt5_service.get_history_deals(date_from, date_to, group=group, ticket=ticket, position=position)
