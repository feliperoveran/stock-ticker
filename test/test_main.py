from main import stock_api, app
from fastapi.testclient import TestClient


def test_ndays(mock_api_response):
    response = mock_api_response.client.get("/ndays")

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


def test_ndays_api_exception(mock_api_error_response):
    # reset stock_api cache to force a re-fetch and mock the failed data
    stock_api.last_refreshed = None

    response = mock_api_error_response.client.get("/ndays")

    assert response.status_code == 500

    assert response.json() == {
        "detail": "An internal error occurred. Please check the logs for details.",
        "instance": "Stock Ticker",
        "status": 500,
        "title": "Internal Error",
        "type": "/ndays"
    }


def test_healthz(mock_api_response):
    response = mock_api_response.client.get("/healthz")

    assert response.status_code == 200

    assert response.json() == {
        "detail": "API health check",
        "instance": "Stock Ticker",
        "status": 200,
        "title": "Health check",
        "type": "/healthz"
    }


def test_prometheus_metrics():
    # use as a context manager so the "startup" event handler will run
    with TestClient(app) as client:
        prom_response = client.get("/metrics")

        assert prom_response.status_code == 200
