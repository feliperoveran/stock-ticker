from fastapi.testclient import TestClient
from main import app

import requests_mock
import json
import os


client = TestClient(app)


def test_ndays(monkeypatch):
    api_host = os.getenv("STOCKS_API_HOST")
    api_key = os.getenv("STOCKS_API_KEY")
    symbol = os.getenv("SYMBOL")
    api_url = f"{api_host}/query?apikey={api_key}&function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}"

    with requests_mock.Mocker(real_http=True) as m:
        m.register_uri(
            "GET",
            api_url,
            json=json.loads(open("fixtures/response.json").read())
        )

        response = client.get("/ndays")

    assert response.status_code == 200

    assert response.json() == {
        "average_closing_price": 259.91,
        "symbol": "BESTSTOCK",
        "ndays": "3",
        "daily_data": {
            "2023-02-06": {
                "open": 257.44,
                "high": 258.3,
                "low": 254.78,
                "close": 256.77,
                "adjusted_close": 256.77,
                "volume": 22485906,
                "dividend_amount": 0,
                "split_coefficient": 1
            },
            "2023-02-03": {
                "open": 259.542,
                "high": 264.2,
                "low": 257.1,
                "close": 258.35,
                "adjusted_close": 258.35,
                "volume": 29077256,
                "dividend_amount": 0,
                "split_coefficient": 1
            },
            "2023-02-02": {
                "open": 258.82,
                "high": 264.69,
                "low": 257.25,
                "close": 264.6,
                "adjusted_close": 264.6,
                "volume": 39940437,
                "dividend_amount": 0,
                "split_coefficient": 1
            }
        }
    }


def test_ndays_api_invalid_response():
    api_host = os.getenv("STOCKS_API_HOST")
    api_key = os.getenv("STOCKS_API_KEY")
    symbol = os.getenv("SYMBOL")
    api_url = f"{api_host}/query?apikey={api_key}&function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}"

    with requests_mock.Mocker(real_http=True) as m:
        m.register_uri(
            "GET",
            api_url,
            json={
                "invalid": "response"
            }
        )

        response = client.get("/ndays")

    assert response.json() == {
        "detail": "An internal error occurred. Please check the logs for details.",
        "instance": "Stock Ticker",
        "status": 500,
        "title": "Internal Error",
        "type": "/ndays"
    }


def test_ndays_api_failure():
    api_host = os.getenv("STOCKS_API_HOST")
    api_key = os.getenv("STOCKS_API_KEY")
    symbol = os.getenv("SYMBOL")
    api_url = f"{api_host}/query?apikey={api_key}&function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}"

    with requests_mock.Mocker(real_http=True) as m:
        m.register_uri(
            "GET",
            api_url,
            status_code=401
        )

        response = client.get("/ndays")

    assert response.status_code == 500

    assert response.json() == {
        "detail": "An internal error occurred. Please check the logs for details.",
        "instance": "Stock Ticker",
        "status": 500,
        "title": "Internal Error",
        "type": "/ndays"
    }
