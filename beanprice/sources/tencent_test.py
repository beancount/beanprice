from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from beanprice.sources import tencent


def payload(rows, **extra):
    return {"code": 0, "data": {"hk02020": {"day": rows, **extra}}}


def test_close_not_open_and_no_future_price():
    response = Mock(status_code=200)
    response.json.return_value = payload([
        ["2026-09-10", "73.550", "72.050"],
        ["2026-09-11", "72.050", "72.450"],
    ])
    with patch.object(tencent.requests, "get", return_value=response) as get:
        quote = tencent.Source().get_historical_price(
            "02020", datetime(2026, 9, 10, 23, tzinfo=tencent.TIMEZONE))
    assert quote.price == Decimal("72.050")
    assert quote.quote_currency == "HKD"
    assert quote.time.date().isoformat() == "2026-09-10"
    assert get.call_args.kwargs["params"]["param"].endswith(",500,")


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-1", "0", "invalid"])
def test_bad_close(value):
    with pytest.raises(ValueError):
        tencent._parse(payload([["2026-09-11", "1", value]]), "hk02020", "HKD")


def test_adjusted_series_cannot_be_used():
    with pytest.raises(ValueError):
        tencent._parse({"code": 0, "data": {"hk02020": {
            "qfqday": [["2026-09-11", "1", "2"]]}}}, "hk02020", "HKD")


def test_currency_metadata_mismatch():
    with pytest.raises(ValueError):
        tencent._parse(payload([["2026-09-11", "1", "2"]],
                              qt={"hk02020": ["100", "ANTA", "02020", "CNY"]}),
                       "hk02020", "HKD")
