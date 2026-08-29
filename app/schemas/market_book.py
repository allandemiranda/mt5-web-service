from pydantic import BaseModel


class BookInfoItem(BaseModel):
    type: int
    price: float
    volume: int
    volume_dbl: float
