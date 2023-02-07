from fastapi import FastAPI, Response, status
from typing import Union
from models import (
    NDaysResponse,
    DailyData,
    Problem,
)

import logging
import os
import sys
import requests


logging.basicConfig(stream=sys.stdout, level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger()

app = FastAPI(
    title="Stock Ticker",
    root_path="/stock-ticker/",
    version="0.0.1",
)


@app.get(
    '/ndays',
    response_model=NDaysResponse,
    responses={'default': {'model': Problem}},
)
async def get_ndays_average(
    response: Response
) -> Union[NDaysResponse, Problem]:
    """
    Response
    """
    # get variables from the env
    api_host = os.getenv("STOCKS_API_HOST")
    api_key = os.getenv("STOCKS_API_KEY")
    symbol = os.getenv("SYMBOL")
    ndays = int(os.getenv("NDAYS"))

    # log values
    logger.debug("API_HOST: {api_host}")
    logger.debug("API_KEY: {api_key}")
    logger.debug("SYMBOL: {symbol}")
    logger.debug("NDAYS: {ndays}")

    # call the API and get the stock data
    api_url = f"{api_host}/query?apikey={api_key}&function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}"
    response = requests.get(api_url)
    response_json = response.json()
    timeseries = response_json["Time Series (Daily)"]

    # get data
    dates = list(timeseries.keys())[:ndays]
    logger.info(f"Will get data for days: {dates}")

    # get all data
    data = {date: timeseries[date] for date in dates}
    logger.info(f"Data: {data}")

    # closing price average
    DATA_CLOSING_PRICE_KEY = "4. close"
    prices = [float(day_data[DATA_CLOSING_PRICE_KEY]) for day_data in data.values()]
    average = sum(prices) / ndays
    logger.info(f"Prices: {prices}")
    logger.info(f"Average price: {average}")

    response.status_code = status.HTTP_200_OK

    return NDaysResponse(
        average_closing_price=round(average, 2),
        symbol=os.getenv("SYMBOL"),
        ndays=os.getenv("NDAYS"),
        daily_data={
            date: DailyData(
                open=data[date]["1. open"],
                high=data[date]["2. high"],
                low=data[date]["3. low"],
                close=data[date]["4. close"],
                adjusted_close=data[date]["5. adjusted close"],
                volume=data[date]["6. volume"],
                dividend_amount=data[date]["7. dividend amount"],
                split_coefficient=data[date]["8. split coefficient"]
            ) for date in dates
        }
    )
