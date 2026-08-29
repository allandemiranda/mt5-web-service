from fastapi import HTTPException, status
from app.core.mt5_manager import mt5_manager


def require_mt5_connection():
    """Dependency that enforces MT5 connection availability.
    
    If MT5 is disconnected or reconnecting, raises HTTP 503 Service Unavailable.
    """
    if not mt5_manager.is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "MT5_SERVICE_UNAVAILABLE",
                "message": "MetaTrader 5 connection is currently unavailable. Automatic reconnection is in progress.",
                "state": mt5_manager.state.value,
                "reconnect_attempts": mt5_manager.reconnect_attempts,
                "last_error": mt5_manager.last_error,
                "last_error_code": mt5_manager.last_error_code,
            },
        )
    return mt5_manager
