from typing import Optional
from pydantic import BaseModel


class PositionInfo(BaseModel):
    ticket: int
    time: int
    time_msc: int
    time_update: int
    time_update_msc: int
    type: int
    magic: int
    identifier: int
    reason: int
    volume: float
    price_open: float
    sl: float
    tp: float
    price_current: float
    swap: float
    profit: float
    symbol: str
    comment: str
    external_id: str


class PositionCloseRequest(BaseModel):
    ticket: int
    deviation: int = 10
    comment: Optional[str] = "Close position via API"
