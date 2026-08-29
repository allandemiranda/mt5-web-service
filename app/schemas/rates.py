from typing import Optional
from pydantic import BaseModel


class RateBar(BaseModel):
    time: int
    time_iso: Optional[str] = None
    open: float
    high: float
    low: float
    close: float
    tick_volume: int
    spread: int
    real_volume: int
