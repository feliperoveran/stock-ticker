from fastapi import FastAPI, Response, status
from typing import Union
from models import (
    NDaysResponse,
    DailyData,
    Problem,
)
from src.stock_api import StockApi
from prometheus_fastapi_instrumentator import Instrumentator

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

# Singleton so we can cache the response
stock_api = StockApi()


# Enable prometheus instrumentation to expose metrics under /metrics
@app.on_event("startup")
async def startup():
    Instrumentator(env_var_name="ENABLE_METRICS").instrument(app).expose(app)


@app.get('/ndays')
def get_ndays_average(
    response: Response
) -> Union[NDaysResponse, Problem]:
    """
    Response
    """
    try:
        ndays_timeseries_data = stock_api.ndays_timeseries_data()
    except Exception as exception:
        logger.error(f"An exception occurred: {exception}")

        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Problem(
            type="/ndays",
            title="Internal Error",
            status=500,
            detail="An internal error occurred. Please check the logs for details.",
            instance=app.title
        )

    average = stock_api.average_closing_price(ndays_timeseries_data)

    response.status_code = status.HTTP_200_OK

    return NDaysResponse(
        average_closing_price=average,
        symbol=stock_api.symbol,
        ndays=stock_api.ndays,
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
