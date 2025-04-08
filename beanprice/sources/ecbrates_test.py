import unittest
from datetime import datetime
from decimal import Decimal
from unittest import mock
import requests
from dateutil import tz
from beanprice import source
from beanprice.sources import ecbrates


ECB_CSV = """KEY,FREQ,CURRENCY,CURRENCY_DENOM,EXR_TYPE,EXR_SUFFIX,TIME_PERIOD,OBS_VALUE,OBS\
_STATUS,OBS_CONF,OBS_PRE_BREAK,OBS_COM,TIME_FORMAT,BREAKS,COLLECTION,COMPILING_ORG,DISS_ORG\
,DOM_SER_IDS,PUBL_ECB,PUBL_MU,PUBL_PUBLIC,UNIT_INDEX_BASE,COMPILATION,COVERAGE,DECIMALS,NAT\
_TITLE,SOURCE_AGENCY,SOURCE_PUB,TITLE,TITLE_COMPL,UNIT,UNIT_MULT
EXR.D.SEK.EUR.SP00.A,D,SEK,EUR,SP00,A,2024-12-24,11.5335,A,F,,,P1D,,A,,,,,,,,,,4,,4F0,,Euro\
/Swedish krona,"ECB reference exchange rate, Euro/Swedish krona, 2:15 pm (C.E.T.)",SEK,0
"""

ECB_CSV_HIST = """KEY,FREQ,CURRENCY,CURRENCY_DENOM,EXR_TYPE,EXR_SUFFIX,TIME_PERIOD,OBS_VALU\
E,OBS_STATUS,OBS_CONF,OBS_PRE_BREAK,OBS_COM,TIME_FORMAT,BREAKS,COLLECTION,COMPILING_ORG,DIS\
S_ORG,DOM_SER_IDS,PUBL_ECB,PUBL_MU,PUBL_PUBLIC,UNIT_INDEX_BASE,COMPILATION,COVERAGE,DECIMAL\
S,NAT_TITLE,SOURCE_AGENCY,SOURCE_PUB,TITLE,TITLE_COMPL,UNIT,UNIT_MULT
EXR.D.SEK.EUR.SP00.A,D,SEK,EUR,SP00,A,2024-12-06,11.523,A,F,,,P1D,,A,,,,,,,,,,4,,4F0,,Euro/\
Swedish krona,"ECB reference exchange rate, Euro/Swedish krona, 2:15 pm (C.E.T.)",SEK,0
"""


def response(contents, status_code=requests.codes.ok):
    """Return a context manager to patch a CSV response."""
    response = mock.Mock()
    response.status_code = status_code
    response.text = contents
    return mock.patch("requests.get", return_value=response)


class ECBRatesErrorFetcher(unittest.TestCase):
    def test_error_invalid_ticker(self):
        with self.assertRaises(ValueError) as exc:
            ecbrates.Source().get_latest_price("INVALID")

    def test_error_network(self):
        with response("Foobar", 404):
            with self.assertRaises(ValueError) as exc:
                ecbrates.Source().get_latest_price("EUR-SEK")

    def test_empty_response(self):
        with response("", 200):
            with self.assertRaises(ecbrates.ECBRatesError) as exc:
                ecbrates.Source().get_latest_price("EUR-SEK")

    def test_valid_response(self):
        contents = ECB_CSV
        with response(contents):
            srcprice = ecbrates.Source().get_latest_price("EUR-SEK")
            self.assertIsInstance(srcprice, source.SourcePrice)
            self.assertEqual(Decimal("11.5335"), srcprice.price)
            self.assertEqual("SEK", srcprice.quote_currency)
            self.assertIsInstance(srcprice.time, datetime)
            self.assertEqual(
                datetime(2024, 12, 24, 0, 0, 0, tzinfo=tz.tzutc()), srcprice.time
            )

    def test_historical_price(self):
        time = datetime(2024, 12, 6, 16, 0, 0, tzinfo=tz.tzlocal()).astimezone(
            tz.tzutc()
        )
        contents = ECB_CSV_HIST
        with response(contents):
            srcprice = ecbrates.Source().get_historical_price("EUR-SEK", time)
            self.assertIsInstance(srcprice, source.SourcePrice)
            self.assertEqual(Decimal("11.523"), srcprice.price)
            self.assertEqual("SEK", srcprice.quote_currency)
            self.assertIsInstance(srcprice.time, datetime)
            self.assertEqual(
                datetime(2024, 12, 6, 0, 0, 0, tzinfo=tz.tzutc()), srcprice.time
            )


if __name__ == "__main__":
    unittest.main()
