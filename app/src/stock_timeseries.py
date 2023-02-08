import logging


logger = logging.getLogger(__name__)


class StockTimeseries():
    def __init__(self, timeseries_data):
        try:
            self.open = timeseries_data["1. open"]
            self.high = timeseries_data["2. high"]
            self.low = timeseries_data["3. low"]
            self.close = timeseries_data["4. close"]
            self.adjusted_close = timeseries_data["5. adjusted close"]
            self.volume = timeseries_data["6. volume"]
            self.dividend_amount = timeseries_data["7. dividend amount"]
            self.split_coefficient = timeseries_data["8. split coefficient"]
        except KeyError as e:
            key = e.args[0]

            logger.error(f"Error when parsing the timeseries data. Key '{key}' is missing from the response!")

            raise StockTimeseriesDeserializeException(key)


class StockTimeseriesDeserializeException(Exception):
    def __init__(self, key):
        super().__init__(f"Key '{key}' is not present in timeseries data.")
