
__copyright__ = "Copyright (C) 2026  Roman Medvedev"
__license__ = "GNU GPLv2"

import datetime
from decimal import Decimal
import unittest
from unittest import mock

from beanprice.sources import ft

class TestFTSource(unittest.TestCase):
    def setUp(self):
        self.source = ft.Source()

    @mock.patch('beanprice.sources.ft.get_url')
    @mock.patch('beanprice.sources.ft.post_json')
    def test_get_latest_price(self, mock_post, mock_get):
        # Mock _get_xid
        mock_get.return_value = 'var xid = "123456";'

        # Mock _fetch_history response
        mock_post.return_value = """
        {
            "Dates": ["2025-12-29T00:00:00"],
            "Elements": [
                {
                    "Type": "price",
                    "ComponentSeries": [
                        {
                            "Type": "Close",
                            "Values": [123.45]
                        }
                    ]
                }
            ]
        }
        """

        price = self.source.get_latest_price("TEST:EXCH")

        self.assertIsNotNone(price)
        self.assertEqual(price.price, Decimal("123.45"))
        self.assertEqual(
            price.time,
            datetime.datetime(2025, 12, 29, 0, 0, 0, tzinfo=datetime.timezone.utc)
        )

    @mock.patch('beanprice.sources.ft.get_url')
    @mock.patch('beanprice.sources.ft.post_json')
    def test_get_historical_price_naive(self, mock_post, mock_get):
        """Test get_historical_price with a naive datetime."""
        mock_get.return_value = 'var xid = "123456";'

        # Return a date slightly before the requested date
        mock_post.return_value = """
        {
            "Dates": ["2025-12-28T00:00:00"],
            "Elements": [
                {
                    "Type": "price",
                    "ComponentSeries": [
                        {
                            "Type": "Close",
                            "Values": [120.00]
                        }
                    ]
                }
            ]
        }
        """

        # Requesting 2025-12-29 (Naive)
        time_naive = datetime.datetime(2025, 12, 29)
        price = self.source.get_historical_price("TEST:EXCH", time_naive)

        self.assertIsNotNone(price)
        self.assertEqual(price.price, Decimal("120.00"))
        # Result should be aware (UTC)
        self.assertEqual(
            price.time,
            datetime.datetime(2025, 12, 28, 0, 0, 0, tzinfo=datetime.timezone.utc)
        )

    @mock.patch('beanprice.sources.ft.get_url')
    @mock.patch('beanprice.sources.ft.post_json')
    def test_get_historical_price_aware(self, mock_post, mock_get):
        """Test get_historical_price with an aware datetime."""
        mock_get.return_value = 'var xid = "123456";'

        # Return a date slightly before the requested date
        mock_post.return_value = """
        {
            "Dates": ["2025-12-28T00:00:00"],
            "Elements": [
                {
                    "Type": "price",
                    "ComponentSeries": [
                        {
                            "Type": "Close",
                            "Values": [120.00]
                        }
                    ]
                }
            ]
        }
        """

        # Requesting 2025-12-29 (Aware UTC)
        time_aware = datetime.datetime(2025, 12, 29, tzinfo=datetime.timezone.utc)
        price = self.source.get_historical_price("TEST:EXCH", time_aware)

        self.assertIsNotNone(price)
        self.assertEqual(price.price, Decimal("120.00"))

    @mock.patch('beanprice.sources.ft.get_url')
    def test_get_xid_regex_variations(self, mock_get):
        """Test different variations of XID format in tearsheet."""
        # Standard
        mock_get.return_value = 'data-mod-config="{xid: \'123456\'}"'
        self.assertEqual(self.source._get_xid("A"), "123456")

        # With quotes
        self.source._xid_cache.clear()
        mock_get.return_value = 'xid="654321"'
        self.assertEqual(self.source._get_xid("B"), "654321")

        # HTML encoded
        self.source._xid_cache.clear()
        mock_get.return_value = '&quot;xid&quot;:&quot;987654&quot;'
        self.assertEqual(self.source._get_xid("C"), "987654")

if __name__ == '__main__':
    unittest.main()
