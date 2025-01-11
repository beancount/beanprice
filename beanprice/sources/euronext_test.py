import datetime
from decimal import Decimal
import unittest

from unittest import mock
from dateutil import tz

import requests

from beanprice.sources import euronext


def response(contents: str, status_code: int = requests.codes.ok):
    """Return a context manager to patch a JSON response."""
    response = mock.Mock()
    response.status_code = status_code
    response.text = contents
    return mock.patch("requests.get", return_value=response)

class EuronextSourceTest(unittest.TestCase):
    def test_error_nextwork(self):
        with response('', 404):
            with self.assertRaises(euronext.EuronextError):
                euronext.Source().get_latest_price('IE00B3XXRP09-XAMS')

    def test_valid_response_price(self):
        contents = '''"Historical Data"
"From 10/01/2025 to 12/01/2023"
IE00B3XXRP09
Date;Open;High;Low;Last;Close;"Number of Shares";"Number of Trades";Turnover
10/01/2025;100.000;101.000;102.00;103.000;104.000;10000;4000;53245;199.0000'''
        with response(contents):
            time = datetime.datetime(2025, 1, 10, 9, 35, tzinfo=tz.gettz('CET'))
            result = euronext.Source().get_historical_price('IE00B3XXRP09-XAMS', time)
            self.assertEqual(result[0], Decimal('100.000'))
            self.assertEqual(\
                result[1],\
                datetime.datetime(2025, 1, 10, 5, 0, 0, tzinfo=tz.gettz('CET'))\
            )
            self.assertEqual(result[2], 'EUR')

if __name__ == "__main__":
    unittest.main()
