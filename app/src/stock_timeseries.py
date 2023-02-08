import logging


logger = logging.getLogger(__name__)


class StockTimeseries():
    def __init__(self, timeseries_data):
        self.open = timeseries_data["1. open"]
        self.high = timeseries_data["2. high"]
        self.low = timeseries_data["3. low"]
        self.close = timeseries_data["4. close"]
        self.adjusted_close = timeseries_data["5. adjusted close"]
        self.volume = timeseries_data["6. volume"]
        self.dividend_amount = timeseries_data["7. dividend amount"]
        self.split_coefficient = timeseries_data["8. split coefficient"]
