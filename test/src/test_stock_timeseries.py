from src.stock_timeseries import (
    StockTimeseries,
)

import pytest


def test_timeseries_data_parsing():
    timeseries_data = {
      "1. open": "257.44",
      "2. high": "258.3",
      "3. low": "254.78",
      "4. close": "256.77",
      "5. adjusted close": "256.77",
      "6. volume": "22485906",
      "7. dividend amount": "0.0000",
      "8. split coefficient": "1.0"
    }

    stock_timeseries = StockTimeseries(timeseries_data)

    assert stock_timeseries.open == "257.44"
    assert stock_timeseries.high == "258.3"
    assert stock_timeseries.low == "254.78"
    assert stock_timeseries.close == "256.77"
    assert stock_timeseries.adjusted_close == "256.77"
    assert stock_timeseries.volume == "22485906"
    assert stock_timeseries.dividend_amount == "0.0000"
    assert stock_timeseries.split_coefficient == "1.0"
