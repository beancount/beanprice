import datetime
import unittest
from decimal import Decimal

from unittest import mock
from dateutil import tz

import requests

from beanprice import source
from beanprice.sources import coincap

timezone = tz.gettz("Europe/Amsterdam")

response_assets_bitcoin_historical = {
    "data": [
        {
            "priceUsd": "32263.2648195597839546",
            "time": 1609804800000,
            "date": "2021-01-05T00:00:00.000Z",
        },
        {
            "priceUsd": "34869.7692419204775049",
            "time": 1609891200000,
            "date": "2021-01-06T00:00:00.000Z",
        },
    ],
    "timestamp": 1618220568799,
}

response_assets_bitcoin = {
    "data": {
        "id": "bitcoin",
        "rank": "1",
        "symbol": "BTC",
        "name": "Bitcoin",
        "supply": "18672456.0000000000000000",
        "maxSupply": "21000000.0000000000000000",
        "marketCapUsd": "1134320211245.9295410753733840",
        "volumeUsd24Hr": "16998481452.4370929843940509",
        "priceUsd": "60748.3135183678858890",
        "changePercent24Hr": "1.3457951950518293",
        "vwap24Hr": "59970.0332730340881967",
        "explorer": "https://blockchain.info/",
    },
    "timestamp": 1618218375359,
}

response_bitcoin_history = {
    "data": [
        {
            "priceUsd": "29232.6707650537687673",
            "time": 1609459200000,
            "date": "2021-01-01T00:00:00.000Z",
        },
        {
            "priceUsd": "30688.0967118388768791",
            "time": 1609545600000,
            "date": "2021-01-02T00:00:00.000Z",
        },
        {
            "priceUsd": "33373.7277104175704785",
            "time": 1609632000000,
            "date": "2021-01-03T00:00:00.000Z",
        },
        {
            "priceUsd": "31832.6862288485383625",
            "time": 1609718400000,
            "date": "2021-01-04T00:00:00.000Z",
        },
        {
            "priceUsd": "32263.2648195597839546",
            "time": 1609804800000,
            "date": "2021-01-05T00:00:00.000Z",
        },
        {
            "priceUsd": "34869.7692419204775049",
            "time": 1609891200000,
            "date": "2021-01-06T00:00:00.000Z",
        },
        {
            "priceUsd": "38041.0026368820979411",
            "time": 1609977600000,
            "date": "2021-01-07T00:00:00.000Z",
        },
        {
            "priceUsd": "39821.5432664411153366",
            "time": 1610064000000,
            "date": "2021-01-08T00:00:00.000Z",
        },
    ],
    "timestamp": 1618219315479,
}


def response(content, status_code=requests.codes.ok):
    """Return a context manager to patch a JSON response."""
    response = mock.Mock()
    response.status_code = status_code
    response.text = ""
    response.json.return_value = content
    return mock.patch("requests.get", return_value=response)


class Source(unittest.TestCase):
    def test_get_latest_price(self):
        with response(content=response_assets_bitcoin):
            srcprice = coincap.Source().get_latest_price("bitcoin")
            self.assertIsInstance(srcprice, source.SourcePrice)
            self.assertEqual(Decimal("60748.3135183678858890"), srcprice.price)
            self.assertEqual(
                datetime.datetime(2021, 4, 12)
                .replace(tzinfo=datetime.timezone.utc)
                .date(),
                srcprice.time.date(),
            )
            self.assertEqual("USD", srcprice.quote_currency)

    def test_get_historical_price(self):
        with response(content=response_assets_bitcoin_historical):
            srcprice = coincap.Source().get_historical_price(
                "bitcoin", datetime.datetime(2021, 1, 6).replace(tzinfo=timezone)
            )
            self.assertEqual(Decimal("34869.7692419204775049"), srcprice.price)
            self.assertEqual(
                datetime.datetime(2021, 1, 6)
                .replace(tzinfo=datetime.timezone.utc)
                .date(),
                srcprice.time.date(),
            )
            self.assertEqual("USD", srcprice.quote_currency)

    def test_get_prices_series(self):
        with response(content=response_bitcoin_history):
            srcprices = coincap.Source().get_prices_series(
                "bitcoin",
                datetime.datetime(2021, 1, 1).replace(tzinfo=timezone),
                datetime.datetime(2021, 3, 20).replace(tzinfo=timezone),
            )
            self.assertEqual(len(srcprices), 8)
            self.assertEqual(Decimal("29232.6707650537687673"), srcprices[0].price)
            self.assertEqual(
                datetime.datetime(2021, 1, 1)
                .replace(tzinfo=datetime.timezone.utc)
                .date(),
                srcprices[0].time.date(),
            )
            self.assertEqual("USD", srcprices[0].quote_currency)


if __name__ == "__main__":
    unittest.main()
