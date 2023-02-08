from src.stock_api import (
    StockApi,
    StockApiException,
    StockApiUnsupportedApiResponseException,
    TIMESERIES_KEY
)

import json
import pytest


"""
fetch_data
"""


def test_fetch_data(mock_api_response):
    api_response = json.loads(open("fixtures/response.json").read())

    fetched_data = StockApi().fetch_data()

    assert fetched_data == api_response


def test_fetch_data_cache(mock_api_response):
    api_response = json.loads(open("fixtures/response.json").read())

    # initialize the singleton
    stock_api = StockApi()

    # call a couple of times to check if cache has been used
    stock_api.fetch_data()
    stock_api.fetch_data()
    stock_api.fetch_data()
    fetched_data = stock_api.fetch_data()

    assert fetched_data == api_response

    # Check that the URL has been called once time and not 4 times
    assert len(mock_api_response.mock.request_history) == 1


def test_fetch_data_api_error(mock_api_error_response):
    with pytest.raises(StockApiException) as exception:
        StockApi().fetch_data()

    assert "Error occurred when calling the API" in exception.value.args[0]


"""
timeseries_data
"""


def test_timeseries_data(mocker):
    mocked_response = {
        TIMESERIES_KEY: {
            "fake": "data"
        }
    }

    mocker.patch(
        "src.stock_api.StockApi.fetch_data",
        lambda _: mocked_response
    )

    assert StockApi().timeseries_data() == mocked_response[TIMESERIES_KEY]


def test_timeseries_data_missing_key(mocker):
    mocker.patch(
        "src.stock_api.StockApi.fetch_data",
        lambda _: {}
    )

    with pytest.raises(StockApiUnsupportedApiResponseException) as exception:
        StockApi().timeseries_data()

    assert f"Key '{TIMESERIES_KEY}' is not present" in exception.value.args[0]


"""
ndays_timeseries_data
"""


def test_ndays_timeseries_data(mocker, monkeypatch):
    mocked_response = {
        "2023-02-06": {
            "1. open": "257.44",
            "2. high": "258.3",
            "3. low": "254.78",
            "4. close": "256.77",
            "5. adjusted close": "256.77",
            "6. volume": "22485906",
            "7. dividend amount": "0.0000",
            "8. split coefficient": "1.0"
        },
        "2023-02-03": {
            "1. open": "259.542",
            "2. high": "264.2",
            "3. low": "257.1",
            "4. close": "258.35",
            "5. adjusted close": "258.35",
            "6. volume": "29077256",
            "7. dividend amount": "0.0000",
            "8. split coefficient": "1.0"
        },
        "2023-02-02": {
            "1. open": "258.82",
            "2. high": "264.69",
            "3. low": "257.25",
            "4. close": "264.6",
            "5. adjusted close": "264.6",
            "6. volume": "39940437",
            "7. dividend amount": "0.0000",
            "8. split coefficient": "1.0"
        }
    }

    mocker.patch(
        "src.stock_api.StockApi.timeseries_data",
        lambda _: mocked_response
    )

    ndays_timeseries_data = StockApi(ndays=2).ndays_timeseries_data()

    expected_keys = ["2023-02-06", "2023-02-03"]

    assert list(ndays_timeseries_data.keys()) == expected_keys

    # make sure the attributes (vars) of the objects are equal to the values of the mocked response
    # regardless of the class or the attribute names
    for key in expected_keys:
        assert list(vars(ndays_timeseries_data[key]).values()) == list(mocked_response[key].values())


"""
average_closing_price
"""


def test_average_closing_price(mocker):
    class MockTimeseriesData():
        def __init__(self, close):
            self.close = close

    ndays_timeseries_data = {
        "2023-02-06": MockTimeseriesData(10),
        "2023-02-05": MockTimeseriesData(15),
        "2023-02-04": MockTimeseriesData(10),
    }

    assert StockApi(ndays=3).average_closing_price(ndays_timeseries_data) == 11.67
