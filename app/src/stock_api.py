from src.stock_timeseries import StockTimeseries
from requests.exceptions import HTTPError

import logging
import os
import requests


TIMESERIES_KEY = "Time Series (Daily)"

logger = logging.getLogger(__name__)


class StockApi():
    def __init__(
        self,
        api_host=os.getenv("STOCKS_API_HOST"),
        api_key=os.getenv("STOCKS_API_KEY"),
        symbol=os.getenv("SYMBOL"),
        ndays=int(os.getenv("NDAYS"))
    ):
        self.api_host = api_host
        self.api_key = api_key
        self.symbol = symbol
        self.ndays = ndays

    def fetch_data(self):
        # call the API and get the stock data
        url = f"{self.api_host}/query?apikey={self.api_key}&function=TIME_SERIES_DAILY_ADJUSTED&symbol={self.symbol}"

        logger.info("Calling API at {}".format(url.replace(self.api_key, "<redacted>")))

        response = requests.get(url)

        try:
            response.raise_for_status()
        except HTTPError as exception:
            raise StockApiException(self.api_host, exception)

        return response.json()

    def timeseries_data(self):
        api_response = self.fetch_data()

        try:
            return api_response[TIMESERIES_KEY]
        except KeyError as e:
            key = e.args[0]

            logger.error(f"Error when parsing the API response. Key '{key}' is missing!")

            raise StockApiUnsupportedApiResponseException(key)

    def ndays_timeseries_data(self):
        timeseries_data = self.timeseries_data()

        dates = list(timeseries_data.keys())[:self.ndays]
        logger.debug(f"Will get data for days: {dates}")

        ndays_data = {date: StockTimeseries(timeseries_data[date]) for date in dates}

        return ndays_data

    def average_closing_price(self):
        ndays_timeseries_data = self.ndays_timeseries_data()

        prices = [float(day_data.close) for day_data in ndays_timeseries_data.values()]

        return sum(prices) / self.ndays


class StockApiException(Exception):
    def __init__(self, host, exception):
        super().__init__(f"Error occurred when calling the API at {host}: {exception}")


class StockApiUnsupportedApiResponseException(Exception):
    def __init__(self, key):
        super().__init__(f"Key '{key}' is not present in API response.")
