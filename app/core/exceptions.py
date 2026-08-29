from fastapi import Request, status
from fastapi.responses import JSONResponse


class MT5ServiceException(Exception):
    """Base exception for MT5 operations."""
    def __init__(self, message: str, error_code: int = -1, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class MT5ConnectionUnavailableException(Exception):
    """Raised when an operation is attempted while MT5 is disconnected."""
    def __init__(self, message: str = "MT5 connection is currently unavailable."):
        super().__init__(message)
        self.message = message


async def mt5_service_exception_handler(request: Request, exc: MT5ServiceException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": "MT5_OPERATION_ERROR",
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
        },
    )


async def mt5_unavailable_exception_handler(request: Request, exc: MT5ConnectionUnavailableException):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "success": False,
            "error": "MT5_SERVICE_UNAVAILABLE",
            "message": exc.message,
        },
    )
