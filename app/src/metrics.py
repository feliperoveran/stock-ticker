from prometheus_client import Counter


class PrometheusInstrumentation():
    def __init__(self):
        self.prometheus_cache_hit_counter = Counter(
            "stock_api_cache_hit",
            "Cache hits on the in-memory StockApi singleton cache"
        )


prometheus_custom_metrics = PrometheusInstrumentation()
