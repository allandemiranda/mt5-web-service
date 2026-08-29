from fastapi import APIRouter, Depends
from app.api.dependencies import require_mt5_connection
from app.schemas.account import AccountInfo
from app.services.mt5_service import mt5_service

router = APIRouter(prefix="/account", tags=["Account"], dependencies=[Depends(require_mt5_connection)])


@router.get("", response_model=AccountInfo, summary="Get Current Trading Account Info")
async def get_account():
    return await mt5_service.get_account_info()
