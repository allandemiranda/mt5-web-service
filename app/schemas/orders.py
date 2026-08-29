from typing import Optional
from pydantic import BaseModel, Field
from app.core.constants import (
    MT5OrderFilling,
    MT5OrderTime,
    MT5OrderType,
    MT5TradeAction,
)


class TradeRequest(BaseModel):
    """Trading request sent to MT5 order_send and order_check."""
    action: MT5TradeAction = Field(..., description="Trade action (e.g. 1 for DEAL)")
    symbol: str = Field(..., description="Financial instrument symbol (e.g. 'EURUSD')")
    volume: float = Field(..., description="Order volume in lots (e.g. 0.1)")
    type: MT5OrderType = Field(..., description="Order type (e.g. 0 for BUY, 1 for SELL)")
    price: Optional[float] = Field(None, description="Execution price (required for pending orders)")
    stoplimit: Optional[float] = Field(None, description="StopLimit price level")
    sl: Optional[float] = Field(None, description="Stop Loss price level")
    tp: Optional[float] = Field(None, description="Take Profit price level")
    deviation: int = Field(10, description="Max acceptable deviation in points")
    type_time: MT5OrderTime = Field(MT5OrderTime.ORDER_TIME_GTC, description="Order expiration type")
    expiration: Optional[int] = Field(None, description="Order expiration time (UNIX timestamp)")
    type_filling: MT5OrderFilling = Field(MT5OrderFilling.ORDER_FILLING_IOC, description="Order filling type")
    comment: Optional[str] = Field(None, description="Order comment")
    position: Optional[int] = Field(None, description="Position ticket for closing/modifying")
    position_by: Optional[int] = Field(None, description="Opposite position ticket for close_by")
    magic: Optional[int] = Field(0, description="Expert Advisor magic ID")


class OrderCheckResult(BaseModel):
    retcode: int
    balance: float
    equity: float
    profit: float
    margin: float
    margin_free: float
    margin_level: float
    comment: str


class OrderSendResult(BaseModel):
    retcode: int
    deal: int
    order: int
    volume: float
    price: float
    bid: float
    ask: float
    comment: str
    request_id: int
    retcode_external: int


class OrderInfo(BaseModel):
    ticket: int
    time_setup: int
    time_setup_msc: int
    time_expiration: int
    type: int
    type_time: int
    type_filling: int
    state: int
    magic: int
    position_id: int
    position_by_id: int
    reason: int
    volume_initial: float
    volume_current: float
    price_open: float
    sl: float
    tp: float
    price_current: float
    price_stoplimit: float
    symbol: str
    comment: str
    external_id: str


class CalcMarginRequest(BaseModel):
    action: MT5OrderType
    symbol: str
    volume: float
    price: float


class CalcProfitRequest(BaseModel):
    action: MT5OrderType
    symbol: str
    volume: float
    price_open: float
    price_close: float
