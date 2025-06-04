from typing import Iterable

from prometheus_client import Metric
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector


class Colector(Collector):
    def __init__(self, connection) -> None:
        self.connection = connection

    def collect(self) -> Iterable[Metric]:
        yield GaugeMetricFamily("my_gauge", "Help text", value=7)
