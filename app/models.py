from typing import Dict
from pydantic import BaseModel, Field

import datetime


class DailyData(BaseModel):
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float
    volume: int
    dividend_amount: float
    split_coefficient: float


class NDaysResponse(BaseModel):
    average_closing_price: float = Field(
        ...,
        description='Add here',
        example="1.22"
    )
    symbol: str = Field(
        ...,
        description="Stock symbol",
        example="MSFT"
    )
    ndays: str = Field(
        ...,
        description="Number of days to lookback in order to return stock data",
        example="7"
    )
    daily_data: Dict[datetime.date, DailyData] = Field(
        ...,
        description="Daily data"
    )
