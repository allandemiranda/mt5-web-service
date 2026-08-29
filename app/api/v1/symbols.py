from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.api.dependencies import require_mt5_connection
from app.schemas.symbols import SymbolInfo, SymbolSelectRequest, SymbolTick
from app.services.mt5_service import mt5_service

router = APIRouter(prefix="/symbols", tags=["Symbols & Market Data"], dependencies=[Depends(require_mt5_connection)])


@router.get("/total", response_model=int, summary="Get Total Symbols Count")
async def get_symbols_total():
    return await mt5_service.get_symbols_total()


@router.get("", response_model=List[SymbolInfo], summary="Get List of Symbols")
async def get_symbols(group: Optional[str] = Query(None, description="Wildcard filter group, e.g. '*EUR*', '!*USD*'")):
    return await mt5_service.get_symbols(group)


@router.get("/{symbol}", response_model=SymbolInfo, summary="Get Specification for a Symbol")
async def get_symbol_info(symbol: str):
    return await mt5_service.get_symbol_info(symbol)


@router.get("/{symbol}/tick", response_model=SymbolTick, summary="Get Current Tick for a Symbol")
async def get_symbol_tick(symbol: str):
    return await mt5_service.get_symbol_tick(symbol)


@router.post("/{symbol}/select", summary="Select or Deselect Symbol in MarketWatch")
async def select_symbol(symbol: str, req: SymbolSelectRequest):
    success = await mt5_service.select_symbol(symbol, req.enable)
    return {"symbol": symbol, "selected": success}
