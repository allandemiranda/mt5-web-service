from fastapi import APIRouter, Depends
from app.api.dependencies import require_mt5_connection
from app.schemas.terminal import TerminalInfo, TerminalVersion, MT5LastError
from app.services.mt5_service import mt5_service

router = APIRouter(prefix="/terminal", tags=["Terminal"], dependencies=[Depends(require_mt5_connection)])


@router.get("/version", response_model=TerminalVersion, summary="Get MT5 Terminal Version")
async def get_version():
    return await mt5_service.get_version()


@router.get("/info", response_model=TerminalInfo, summary="Get MT5 Terminal Parameters")
async def get_terminal_info():
    return await mt5_service.get_terminal_info()


@router.get("/last-error", response_model=MT5LastError, summary="Get Last MT5 Error")
async def get_last_error():
    return await mt5_service.get_last_error()
