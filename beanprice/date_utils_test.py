__copyright__ = "Copyright (C) 2020  Martin Blais"
__license__ = "GNU GPLv2"

import unittest
import datetime
import dateutil

from beanprice import date_utils


class TestDateUtils(unittest.TestCase):

    def test_parse_date_liberally(self):
        const_date = datetime.date(2014, 12, 7)
        test_cases = (
            ('12/7/2014',),
            ('7-Dec-2014',),
            ('7/12/2014', {'parserinfo': dateutil.parser.parserinfo(dayfirst=True)}),
            ('12/7', {'default': datetime.datetime(2014, 1, 1)}),
            ('7.12.2014', {'dayfirst': True}),
            ('14 12 7', {'yearfirst': True}),
            ('Transaction of 7th December 2014', {'fuzzy': True}),
        )
        for case in test_cases:
            if len(case) == 2:
                parse_date = date_utils.parse_date_liberally(case[0], case[1])
            else:
                parse_date = date_utils.parse_date_liberally(case[0])
            self.assertEqual(const_date, parse_date)

    def test_intimezone(self):
        with date_utils.intimezone("America/New_York"):
            now_nyc = datetime.datetime.now()
        with date_utils.intimezone("Europe/Berlin"):
            now_berlin = datetime.datetime.now()
        with date_utils.intimezone("Asia/Tokyo"):
            now_tokyo = datetime.datetime.now()
        self.assertNotEqual(now_nyc, now_berlin)
        self.assertNotEqual(now_berlin, now_tokyo)
        self.assertNotEqual(now_tokyo, now_nyc)


if __name__ == '__main__':
    unittest.main()
