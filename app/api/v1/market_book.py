from typing import List
from fastapi import APIRouter, Depends
from app.api.dependencies import require_mt5_connection
from app.schemas.market_book import BookInfoItem
from app.services.mt5_service import mt5_service

router = APIRouter(prefix="/market-book", tags=["Market Depth (DOM)"], dependencies=[Depends(require_mt5_connection)])


@router.post("/{symbol}/subscribe", summary="Subscribe to Market Depth for Symbol")
async def subscribe_market_book(symbol: str):
    success = await mt5_service.market_book_add(symbol)
    return {"symbol": symbol, "subscribed": success}


@router.get("/{symbol}", response_model=List[BookInfoItem], summary="Get Current Market Depth Records")
async def get_market_book(symbol: str):
    return await mt5_service.market_book_get(symbol)


@router.delete("/{symbol}/unsubscribe", summary="Unsubscribe from Market Depth")
async def unsubscribe_market_book(symbol: str):
    success = await mt5_service.market_book_release(symbol)
    return {"symbol": symbol, "unsubscribed": success}
