import unittest
from unittest import mock
import datetime
from dateutil import tz
from dateutil.parser import parse

from decimal import Decimal
from beanprice.sources import csif
from beanprice.source import MissingDate, SourcePrice


def _fetch_response(contents):
    """Return a context manager to patch a JSON response."""
    response = mock.Mock()
    response.status_code = 404
    response.text = ""
    response.json.return_value = contents
    return mock.patch('subprocess.check_output', return_value=response)


class CsifPriceFetcher(unittest.TestCase):
    def test_error_invalid_ticker(self):
        with self.assertRaises(csif.CsifApiError):
            csif.Source().get_latest_price('INVALID')

    def test_error_invalid_date(self):
        with self.assertRaises(MissingDate):
            csif.Source().get_historical_price('CH0030849712', parse("2050-01-01"))

    def test_valid_response(self):
        data = '' \
               '<some gibber>' \
               '        <td>CH0030849712</td>' \
               '        <td>3084971</td>' \
               '        <td>USD</td> ' \
               '        <td>21.03.2022</td>' \
               '        <td>3037.75000</td>' \
               '<more gibber>'

        with _fetch_response(data):
            srcprice: SourcePrice = csif.Source().get_latest_price('CH0030849712')
            self.assertIsInstance(srcprice, SourcePrice)
            self.assertEqual(Decimal('3037.75000'), srcprice.price)
            self.assertEqual('USD', srcprice.quote_currency)
            self.assertEqual(datetime.datetime(2022, 3, 21, 0, 0, 0, tzinfo=tz.gettz('Europe/Zurich')), srcprice.time)
            pass


if __name__ == '__main__':
    unittest.main()
