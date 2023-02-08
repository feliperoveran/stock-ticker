from fastapi.testclient import TestClient
from main import app

import pytest
import os
import json
import requests_mock


class ApiMock():
    def __init__(self, mock, client):
        self.mock = mock
        self.client = client


@pytest.fixture
def mock_api_response():
    api_host = os.getenv("STOCKS_API_HOST")
    api_key = os.getenv("STOCKS_API_KEY")
    symbol = os.getenv("SYMBOL")
    api_url = f"{api_host}/query?apikey={api_key}&function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}"

    api_response = json.loads(open("fixtures/response.json").read())

    with requests_mock.Mocker(real_http=True) as m:
        m.register_uri(
            "GET",
            api_url,
            json=api_response
        )

        yield ApiMock(m, TestClient(app))


@pytest.fixture
def mock_api_error_response():
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

        yield ApiMock(m, TestClient(app))
