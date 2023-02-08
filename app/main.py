from fastapi import FastAPI, Response, status
from typing import Union
from models import (
    NDaysResponse,
    DailyData,
    Problem,
)
from src.stock_api import StockApi

import logging
import os
import sys


logging.basicConfig(stream=sys.stdout, level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger()

app = FastAPI(
    title="Stock Ticker",
    root_path="/stock-ticker/",
    version="0.0.1",
)


@app.get('/ndays')
def get_ndays_average(
    response: Response
) -> Union[NDaysResponse, Problem]:
    """
    Response
    """
    stock_api = StockApi()

    ndays_timeseries_data = stock_api.ndays_timeseries_data()

    average = stock_api.average_closing_price()

    response.status_code = status.HTTP_200_OK

    return NDaysResponse(
        average_closing_price=round(average, 2),
        symbol=os.getenv("SYMBOL"),
        ndays=os.getenv("NDAYS"),
        daily_data={
            date: DailyData(
                open=ndays_timeseries_data[date].open,
                high=ndays_timeseries_data[date].high,
                low=ndays_timeseries_data[date].low,
                close=ndays_timeseries_data[date].close,
                adjusted_close=ndays_timeseries_data[date].adjusted_close,
                volume=ndays_timeseries_data[date].volume,
                dividend_amount=ndays_timeseries_data[date].dividend_amount,
                split_coefficient=ndays_timeseries_data[date].split_coefficient
            ) for date in ndays_timeseries_data.keys()
        }
    )
