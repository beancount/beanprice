from typing import Any

SourcePrice: Any

class Source:
    def get_latest_price(self, ticker: Any) -> None: ...
    def get_historical_price(self, ticker: Any, time: Any) -> None: ...
