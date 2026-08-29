from fastapi import APIRouter
from app.core.mt5_manager import mt5_manager

router = APIRouter(tags=["Health & Status"])


@router.get("/health", summary="Health Check & MT5 Status")
async def health_check():
    """Returns application health status and MT5 terminal diagnostics.
    
    Always accessible regardless of MT5 connection status.
    """
    status_info = mt5_manager.get_status_summary()
    return {
        "status": "healthy" if status_info["is_connected"] else "degraded",
        "mt5": status_info,
    }
