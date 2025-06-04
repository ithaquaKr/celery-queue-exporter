from typing import Iterable

from prometheus_client import Metric
from prometheus_client.core import REGISTRY, GaugeMetricFamily
from prometheus_client.registry import Collector


class CQCollector(Collector):
    def __init__(self) -> None:
        pass

    def collect(self) -> Iterable[Metric]:
        yield GaugeMetricFamily("my_gauge", "Help text", value=7)


REGISTRY.register(CQCollector())
