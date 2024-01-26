"""Tests for main driver for price fetching.
"""
__copyright__ = "Copyright (C) 2015-2020  Martin Blais"
__license__ = "GNU GPLv2"

import datetime
import logging
import shutil
import sys
import tempfile
import types
import unittest
from os import path
from unittest import mock
from decimal import Decimal

from dateutil import tz

from beancount.utils import test_utils
from beancount.parser import cmptest
from beancount import loader

from beanprice.source import SourcePrice
from beanprice import price
from beanprice.sources import yahoo


PS = price.PriceSource
ONE = Decimal(1)


def run_with_args(function, args, runner_file=None):
    """Run the given function with sys.argv set to argv. The first argument is
    automatically inferred to be where the function object was defined. sys.argv
    is restored after the function is called.
    Args:
      function: A function object to call with no arguments.
      argv: A list of arguments, excluding the script name, to be temporarily
        set on sys.argv.
      runner_file: An optional name of the top-level file being run.
    Returns:
      The return value of the function run.
    """
    saved_argv = sys.argv
    saved_handlers = logging.root.handlers

    try:
        if runner_file is None:
            module = sys.modules[function.__module__]
            runner_file = module.__file__
        sys.argv = [runner_file] + args
        logging.root.handlers = []
        return function()
    finally:
        sys.argv = saved_argv
        logging.root.handlers = saved_handlers


class TestCache(unittest.TestCase):

    def test_fetch_cached_price__disabled(self):
        # Latest.
        with mock.patch('beanprice.price._CACHE', None):
            self.assertIsNone(price._CACHE)
            source = mock.MagicMock()
            price.fetch_cached_price(source, 'HOOL', None)
            self.assertTrue(source.get_latest_price.called)

        # Historical.
        with mock.patch('beanprice.price._CACHE', None):
            self.assertIsNone(price._CACHE)
            source = mock.MagicMock()
            price.fetch_cached_price(source, 'HOOL', datetime.date.today())
            self.assertTrue(source.get_historical_price.called)

    def test_fetch_cached_price__latest(self):
        tmpdir = tempfile.mkdtemp()
        tmpfile = path.join(tmpdir, 'prices.cache')
        try:
            price.setup_cache(tmpfile, False)

            srcprice = SourcePrice(Decimal('1.723'), datetime.datetime.now(tz.tzutc()),
                                   'USD')
            source = mock.MagicMock()
            source.get_latest_price.return_value = srcprice
            source.__file__ = '<module>'

            # Cache miss.
            result = price.fetch_cached_price(source, 'HOOL', None)
            self.assertTrue(source.get_latest_price.called)
            self.assertEqual(1, len(price._CACHE))
            self.assertEqual(srcprice, result)

            source.get_latest_price.reset_mock()

            # Cache hit.
            result = price.fetch_cached_price(source, 'HOOL', None)
            self.assertFalse(source.get_latest_price.called)
            self.assertEqual(1, len(price._CACHE))
            self.assertEqual(srcprice, result)

            srcprice2 = SourcePrice(
                Decimal('1.894'), datetime.datetime.now(tz.tzutc()), 'USD')
            source.get_latest_price.reset_mock()
            source.get_latest_price.return_value = srcprice2

            # Cache expired.
            time_beyond = datetime.datetime.now() + price._CACHE.expiration * 2
            with mock.patch('beanprice.price.now', return_value=time_beyond):
                result = price.fetch_cached_price(source, 'HOOL', None)
                self.assertTrue(source.get_latest_price.called)
                self.assertEqual(1, len(price._CACHE))
                self.assertEqual(srcprice2, result)
        finally:
            price.reset_cache()
            if path.exists(tmpdir):
                shutil.rmtree(tmpdir)

    def test_fetch_cached_price__clear_cache(self):
        tmpdir = tempfile.mkdtemp()
        tmpfile = path.join(tmpdir, 'prices.cache')
        try:
            price.setup_cache(tmpfile, False)

            srcprice = SourcePrice(Decimal('1.723'), datetime.datetime.now(tz.tzutc()),
                                   'USD')
            source = mock.MagicMock()
            source.get_latest_price.return_value = srcprice
            source.__file__ = '<module>'

            # Cache miss.
            result = price.fetch_cached_price(source, 'HOOL', None)
            self.assertTrue(source.get_latest_price.called)
            self.assertEqual(1, len(price._CACHE))
            self.assertEqual(srcprice, result)

            source.get_latest_price.reset_mock()

            # Cache hit.
            result = price.fetch_cached_price(source, 'HOOL', None)
            self.assertFalse(source.get_latest_price.called)
            self.assertEqual(1, len(price._CACHE))
            self.assertEqual(srcprice, result)

            srcprice2 = SourcePrice(
                Decimal('1.894'), datetime.datetime.now(tz.tzutc()), 'USD')
            source.get_latest_price.reset_mock()
            source.get_latest_price.return_value = srcprice2

            # Open cache again, but clear it.
            price.reset_cache()
            price.setup_cache(tmpfile, True)

            # Cache cleared.
            result = price.fetch_cached_price(source, 'HOOL', None)
            self.assertTrue(source.get_latest_price.called)
            self.assertEqual(1, len(price._CACHE))
            self.assertEqual(srcprice2, result)
        finally:
            price.reset_cache()
            if path.exists(tmpdir):
                shutil.rmtree(tmpdir)

    def test_fetch_cached_price__historical(self):
        tmpdir = tempfile.mkdtemp()
        tmpfile = path.join(tmpdir, 'prices.cache')
        try:
            price.setup_cache(tmpfile, False)

            srcprice = SourcePrice(
                Decimal('1.723'), datetime.datetime.now(tz.tzutc()), 'USD')
            source = mock.MagicMock()
            source.get_historical_price.return_value = srcprice
            source.__file__ = '<module>'

            # Cache miss.
            day = datetime.date(2006, 1, 2)
            result = price.fetch_cached_price(source, 'HOOL', day)
            self.assertTrue(source.get_historical_price.called)
            self.assertEqual(1, len(price._CACHE))
            self.assertEqual(srcprice, result)

            source.get_historical_price.reset_mock()

            # Cache hit.
            result = price.fetch_cached_price(source, 'HOOL', day)
            self.assertFalse(source.get_historical_price.called)
            self.assertEqual(1, len(price._CACHE))
            self.assertEqual(srcprice, result)
        finally:
            price.reset_cache()
            if path.exists(tmpdir):
                shutil.rmtree(tmpdir)


class TestProcessArguments(unittest.TestCase):

    def test_filename_not_exists(self):
        with test_utils.capture('stderr'):
            with self.assertRaises(SystemExit):
                run_with_args(
                    price.process_args, ['--no-cache', '/some/file.beancount'])

    @test_utils.docfile
    def test_explicit_file__badcontents(self, filename):
        """
        2015-01-01 open Assets:Invest
        2015-01-01 open USD ;; Error
        """
        with test_utils.capture('stderr'):
            args, jobs, _, __ = run_with_args(
                price.process_args, ['--no-cache', filename])
            self.assertEqual([], jobs)

    def test_filename_exists(self):
        with tempfile.NamedTemporaryFile('w') as tmpfile:
            with test_utils.capture('stderr'):
                args, jobs, _, __ = run_with_args(
                    price.process_args, ['--no-cache', tmpfile.name])
                self.assertEqual([], jobs)  # Empty file.

    def test_expressions(self):
        with test_utils.capture('stderr'):
            args, jobs, _, __ = run_with_args(
                price.process_args, ['--no-cache', '-e', 'USD:yahoo/AAPL'])
            self.assertEqual(
                [price.DatedPrice(
                    'AAPL', 'USD', None,
                    [PS(yahoo, 'AAPL', False, ONE)])], jobs)


class TestClobber(cmptest.TestCase):

    @loader.load_doc()
    def setUp(self, entries, _, __):
        """
          ;; Existing file.
          2015-01-05 price HDV                                 75.56 USD
          2015-01-23 price HDV                                 77.34 USD
          2015-02-06 price HDV                                 77.16 USD
          2015-02-12 price HDV                                 78.17 USD
          2015-05-01 price HDV                                 77.48 USD
          2015-06-02 price HDV                                 76.33 USD
          2015-06-29 price HDV                                 73.74 USD
          2015-07-06 price HDV                                 73.79 USD
          2015-08-11 price HDV                                 74.19 USD
          2015-09-04 price HDV                                 68.98 USD
        """
        self.entries = entries

        # New entries.
        self.price_entries, _, __ = loader.load_string("""
          2015-01-27 price HDV                                 76.83 USD
          2015-02-06 price HDV                                 77.16 USD
          2015-02-19 price HDV                                  77.5 USD
          2015-06-02 price HDV                                 76.33 USD
          2015-06-19 price HDV                                    76 USD
          2015-07-06 price HDV                                 73.79 USD
          2015-07-31 price HDV                                 74.64 USD
          2015-08-11 price HDV                                 74.20 USD ;; Different
        """, dedent=True)

    def test_clobber_nodiffs(self):
        new_price_entries, _ = price.filter_redundant_prices(self.price_entries,
                                                             self.entries,
                                                             diffs=False)
        self.assertEqualEntries("""
          2015-01-27 price HDV                                 76.83 USD
          2015-02-19 price HDV                                  77.5 USD
          2015-06-19 price HDV                                    76 USD
          2015-07-31 price HDV                                 74.64 USD
        """, new_price_entries)

    def test_clobber_diffs(self):
        new_price_entries, _ = price.filter_redundant_prices(self.price_entries,
                                                             self.entries,
                                                             diffs=True)
        self.assertEqualEntries("""
          2015-01-27 price HDV                                 76.83 USD
          2015-02-19 price HDV                                  77.5 USD
          2015-06-19 price HDV                                    76 USD
          2015-07-31 price HDV                                 74.64 USD
          2015-08-11 price HDV                                 74.20 USD ;; Different
        """, new_price_entries)


class TestTimezone(unittest.TestCase):

    @mock.patch.object(price, 'fetch_cached_price')
    def test_fetch_price__naive_time_no_timeozne(self, fetch_cached):
        fetch_cached.return_value = SourcePrice(
            Decimal('125.00'), datetime.datetime(2015, 11, 22, 16, 0, 0), 'JPY')
        dprice = price.DatedPrice('JPY', 'USD', datetime.date(2015, 11, 22), None)
        with self.assertRaises(ValueError):
            price.fetch_price(dprice._replace(sources=[
                PS(yahoo, 'USDJPY', False, ONE)]), False)


class TestInverted(unittest.TestCase):

    def setUp(self):
        fetch_cached = mock.patch('beanprice.price.fetch_cached_price').start()
        fetch_cached.return_value = SourcePrice(
            Decimal('125.00'), datetime.datetime(2015, 11, 22, 16, 0, 0,
                                                 tzinfo=tz.tzlocal()),
            'JPY')
        self.dprice = price.DatedPrice('JPY', 'USD', datetime.date(2015, 11, 22),
                                       None)
        self.addCleanup(mock.patch.stopall)

    def test_fetch_price__normal(self):
        entry = price.fetch_price(self.dprice._replace(sources=[
            PS(yahoo, 'USDJPY', False, ONE)]), False)
        self.assertEqual(('JPY', 'USD'), (entry.currency, entry.amount.currency))
        self.assertEqual(Decimal('125.00'), entry.amount.number)

    def test_fetch_price__inverted(self):
        entry = price.fetch_price(self.dprice._replace(sources=[
            PS(yahoo, 'USDJPY', True, ONE)]), False)
        self.assertEqual(('JPY', 'USD'), (entry.currency, entry.amount.currency))
        self.assertEqual(Decimal('0.008'), entry.amount.number)

    def test_fetch_price__swapped(self):
        entry = price.fetch_price(self.dprice._replace(sources=[
            PS(yahoo, 'USDJPY', True, ONE)]), True)
        self.assertEqual(('USD', 'JPY'), (entry.currency, entry.amount.currency))
        self.assertEqual(Decimal('125.00'), entry.amount.number)


class TestMultiplier(unittest.TestCase):

    def test_multiplier(self):
        fetch_cached = mock.patch('beanprice.price.fetch_cached_price').start()
        self.addCleanup(mock.patch.stopall)
        fetch_cached.return_value = SourcePrice(
            Decimal('16824.00'), datetime.datetime(2023, 1, 1, 16, 0, 0,
                                                   tzinfo=tz.tzlocal()),
            None)
        dprice = price.DatedPrice(
            'GBP', 'XSDR', datetime.date(2023, 1, 1), [
                PS(yahoo, 'XSDR.L', False, Decimal('0.01')),
            ])
        entry = price.fetch_price(dprice)
        self.assertEqual(('GBP', 'XSDR'), (entry.currency, entry.amount.currency))
        self.assertEqual('168.2400', str(entry.amount.number))


class TestImportSource(unittest.TestCase):

    def test_import_source_valid(self):
        for name in 'oanda', 'yahoo':
            module = price.import_source(name)
            self.assertIsInstance(module, types.ModuleType)
        module = price.import_source('beanprice.sources.yahoo')
        self.assertIsInstance(module, types.ModuleType)

    def test_import_source_invalid(self):
        with self.assertRaises(ImportError):
            price.import_source('non.existing.module')


class TestParseSource(unittest.TestCase):

    def test_source_invalid(self):
        with self.assertRaises(ValueError):
            price.parse_single_source('AAPL')
        with self.assertRaises(ValueError):
            price.parse_single_source('***//--')

        # The module gets imported at this stage.
        with self.assertRaises(ImportError):
            price.parse_single_source('invalid.module.name/NASDAQ:AAPL')

        # Make sure that an invalid name at the tail doesn't succeed.
        with self.assertRaises(ValueError):
            psource = price.parse_single_source('yahoo/CNYUSD&X')

    def test_source_valid(self):
        psource = price.parse_single_source('yahoo/CNYUSD=X')
        self.assertEqual(PS(yahoo, 'CNYUSD=X', False, ONE), psource)

        psource = price.parse_single_source('beanprice.sources.yahoo/AAPL')
        self.assertEqual(PS(yahoo, 'AAPL', False, ONE), psource)

        psource = price.parse_single_source('0.01*yahoo/XSDR.L')
        self.assertEqual(PS(yahoo, 'XSDR.L', False, Decimal('0.01')), psource)


class TestParseSourceMap(unittest.TestCase):

    def _clean_source_map(self, smap):
        return {currency: [PS(s[0].__name__, s[1], s[2], s[3]) for s in sources]
                for currency, sources in smap.items()}

    def test_source_map_invalid(self):
        for expr in 'USD', 'something else', 'USD:NASDAQ:AAPL':
            with self.assertRaises(ValueError):
                price.parse_source_map(expr)

    def test_source_map_onecur_single(self):
        smap = price.parse_source_map('USD:yahoo/AAPL')
        self.assertEqual(
            {'USD': [PS('beanprice.sources.yahoo', 'AAPL', False, ONE)]},
            self._clean_source_map(smap))

    def test_source_map_onecur_multiple(self):
        smap = price.parse_source_map('USD:oanda/USDCAD,yahoo/CAD=X')
        self.assertEqual(
            {'USD': [PS('beanprice.sources.oanda', 'USDCAD', False, ONE),
                     PS('beanprice.sources.yahoo', 'CAD=X', False, ONE)]},
            self._clean_source_map(smap))

    def test_source_map_manycur_single(self):
        smap = price.parse_source_map('USD:yahoo/USDCAD '
                                      'CAD:yahoo/CAD=X')
        self.assertEqual(
            {'USD': [PS('beanprice.sources.yahoo', 'USDCAD', False, ONE)],
             'CAD': [PS('beanprice.sources.yahoo', 'CAD=X', False, ONE)]},
            self._clean_source_map(smap))

    def test_source_map_manycur_multiple(self):
        smap = price.parse_source_map('USD:yahoo/GBPUSD,oanda/GBPUSD '
                                      'CAD:yahoo/GBPCAD')
        self.assertEqual(
            {'USD': [PS('beanprice.sources.yahoo', 'GBPUSD', False, ONE),
                     PS('beanprice.sources.oanda', 'GBPUSD', False, ONE)],
             'CAD': [PS('beanprice.sources.yahoo', 'GBPCAD', False, ONE)]},
            self._clean_source_map(smap))

    def test_source_map_inverse(self):
        smap = price.parse_source_map('USD:yahoo/^GBPUSD')
        self.assertEqual(
            {'USD': [PS('beanprice.sources.yahoo', 'GBPUSD', True, ONE)]},
            self._clean_source_map(smap))

    def test_source_map_multiplier(self):
        smap = price.parse_source_map(
            'GBP:0.01*yahoo/XSDR.L;GBP:yahoo/XSDR;USD:1000*yahoo/mXSDRUSD')
        print(smap)
        self.assertEqual({
            'GBP': [PS('beanprice.sources.yahoo', 'XSDR.L', False, Decimal('0.01')),
                    PS('beanprice.sources.yahoo', 'XSDR', False, ONE)],
            'USD': [PS('beanprice.sources.yahoo', 'mXSDRUSD', False, Decimal(1000))],

        }, self._clean_source_map(smap))


class TestFilters(unittest.TestCase):

    @loader.load_doc()
    def test_get_price_jobs__date(self, entries, _, __):
        """
        2000-01-10 open Assets:US:Invest:QQQ
        2000-01-10 open Assets:US:Invest:VEA
        2000-01-10 open Assets:US:Invest:Margin

        2014-01-01 commodity QQQ
          price: "USD:yahoo/NASDAQ:QQQ"

        2014-01-01 commodity VEA
          price: "USD:yahoo/NASDAQ:VEA"

        2014-02-06 *
          Assets:US:Invest:QQQ             100 QQQ {86.23 USD}
          Assets:US:Invest:VEA             200 VEA {43.22 USD}
          Assets:US:Invest:Margin

        2014-08-07 *
          Assets:US:Invest:QQQ            -100 QQQ {86.23 USD} @ 91.23 USD
          Assets:US:Invest:Margin

        2015-01-15 *
          Assets:US:Invest:QQQ              10 QQQ {92.32 USD}
          Assets:US:Invest:VEA            -200 VEA {43.22 USD} @ 41.01 USD
          Assets:US:Invest:Margin
        """
        jobs = price.get_price_jobs_at_date(entries, datetime.date(2014, 1, 1),
                                            False, None)
        self.assertEqual(set(), {(job.base, job.quote) for job in jobs})

        jobs = price.get_price_jobs_at_date(entries, datetime.date(2014, 6, 1),
                                            False, None)
        self.assertEqual({('QQQ', 'USD'), ('VEA', 'USD')},
                         {(job.base, job.quote) for job in jobs})

        jobs = price.get_price_jobs_at_date(entries, datetime.date(2014, 10, 1),
                                            False, None)
        self.assertEqual({('VEA', 'USD')},
                         {(job.base, job.quote) for job in jobs})

        jobs = price.get_price_jobs_at_date(entries, None, False, None)
        self.assertEqual({('QQQ', 'USD')}, {(job.base, job.quote) for job in jobs})

    @loader.load_doc()
    def test_get_price_jobs__inactive(self, entries, _, __):
        """
        2000-01-10 open Assets:US:Invest:QQQ
        2000-01-10 open Assets:US:Invest:VEA
        2000-01-10 open Assets:US:Invest:Margin

        2014-01-01 commodity QQQ
          price: "USD:yahoo/NASDAQ:QQQ"

        2014-01-01 commodity VEA
          price: "USD:yahoo/NASDAQ:VEA"

        2014-02-06 *
          Assets:US:Invest:QQQ             100 QQQ {86.23 USD}
          Assets:US:Invest:VEA             200 VEA {43.22 USD}
          Assets:US:Invest:Margin

        2014-08-07 *
          Assets:US:Invest:QQQ            -100 QQQ {86.23 USD} @ 91.23 USD
          Assets:US:Invest:Margin
        """
        jobs = price.get_price_jobs_at_date(entries, None, False, None)
        self.assertEqual({('VEA', 'USD')}, {(job.base, job.quote) for job in jobs})

        jobs = price.get_price_jobs_at_date(entries, None, True, None)
        self.assertEqual({('VEA', 'USD'), ('QQQ', 'USD')},
                         {(job.base, job.quote) for job in jobs})

    @loader.load_doc()
    def test_get_price_jobs__undeclared(self, entries, _, __):
        """
        2000-01-10 open Assets:US:Invest:QQQ
        2000-01-10 open Assets:US:Invest:VEA
        2000-01-10 open Assets:US:Invest:Margin

        2014-01-01 commodity QQQ
          price: "USD:yahoo/NASDAQ:QQQ"

        2014-02-06 *
          Assets:US:Invest:QQQ             100 QQQ {86.23 USD}
          Assets:US:Invest:VEA             200 VEA {43.22 USD}
          Assets:US:Invest:Margin
        """
        jobs = price.get_price_jobs_at_date(entries, None, False, None)
        self.assertEqual({('QQQ', 'USD')}, {(job.base, job.quote) for job in jobs})

        jobs = price.get_price_jobs_at_date(entries, None, False, 'yahoo')
        self.assertEqual({('QQQ', 'USD'), ('VEA', 'USD')},
                         {(job.base, job.quote) for job in jobs})

    @loader.load_doc()
    def test_get_price_jobs__default_source(self, entries, _, __):
        """
        2000-01-10 open Assets:US:Invest:QQQ
        2000-01-10 open Assets:US:Invest:Margin

        2014-01-01 commodity QQQ
          price: "NASDAQ:QQQ"

        2014-02-06 *
          Assets:US:Invest:QQQ             100 QQQ {86.23 USD}
          Assets:US:Invest:Margin
        """
        jobs = price.get_price_jobs_at_date(entries, None, False, 'yahoo')
        self.assertEqual(1, len(jobs[0].sources))
        self.assertIsInstance(jobs[0].sources[0], price.PriceSource)

    @loader.load_doc()
    def test_get_price_jobs__currencies_not_at_cost(self, entries, _, __):
        """
        2000-01-10 open Assets:US:BofA:Checking
        2000-01-10 open Assets:US:BofA:CHF

        2014-01-01 commodity USD
        2014-01-01 commodity CHF
          price: "USD:yahoo/CHFUSD=X"

        2021-01-04 *
          Assets:US:BofA:Checking        100 USD
          Assets:US:BofA:CHF             -110 CHF @@ 100 USD
        """
        # TODO: Shouldn't we actually return (CHF, USD) here?
        jobs = price.get_price_jobs_at_date(entries, datetime.date(2021, 1, 4),
                                            False, None)
        self.assertEqual(set(), {(job.base, job.quote) for job in jobs})

        jobs = price.get_price_jobs_at_date(entries, datetime.date(2021, 1, 6),
                                            False, None)
        self.assertEqual({('CHF', 'USD')}, {(job.base, job.quote) for job in jobs})

        # TODO: Shouldn't we return (CHF, USD) here, as above?
        jobs = price.get_price_jobs_up_to_date(entries, datetime.date(2021, 1, 6),
                                               False, None)
        self.assertEqual(set(), {(job.base, job.quote) for job in jobs})

    @loader.load_doc()
    def test_get_price_jobs_up_to_date(self, entries, _, __):
        """
        2000-01-10 open Assets:US:Invest:QQQ
        2000-01-10 open Assets:US:Invest:VEA
        2000-01-10 open Assets:US:Invest:Margin

        2021-01-01 commodity QQQ
          price: "USD:yahoo/NASDAQ:QQQ"

        2021-01-01 commodity VEA
          price: "USD:yahoo/NASDAQ:VEA"

        2021-01-04 *
          Assets:US:Invest:QQQ             100 QQQ {86.23 USD}
          Assets:US:Invest:VEA             200 VEA {43.22 USD}
          Assets:US:Invest:Margin

        2021-01-05 *
          Assets:US:Invest:QQQ            -100 QQQ {86.23 USD} @ 91.23 USD
          Assets:US:Invest:Margin

        2021-01-07 *
          Assets:US:Invest:QQQ              10 QQQ {92.32 USD}
          Assets:US:Invest:VEA            -200 VEA {43.22 USD} @ 41.01 USD
          Assets:US:Invest:Margin
        """
        jobs = price.get_price_jobs_up_to_date(entries, datetime.date(2021, 1, 8))
        self.assertEqual({
                ('QQQ', 'USD', datetime.date(2021, 1, 4)),
                ('QQQ', 'USD', datetime.date(2021, 1, 5)),
                ('QQQ', 'USD', datetime.date(2021, 1, 7)),
                ('VEA', 'USD', datetime.date(2021, 1, 4)),
                ('VEA', 'USD', datetime.date(2021, 1, 5)),
                ('VEA', 'USD', datetime.date(2021, 1, 6)),
                ('VEA', 'USD', datetime.date(2021, 1, 7)),
            }, {(job.base, job.quote, job.date) for job in jobs})


class TestFromFile(unittest.TestCase):

    @loader.load_doc()
    def setUp(self, entries, _, __):
        """
        2000-01-10 open Assets:US:Investments:QQQ
        2000-01-10 open Assets:CA:Investments:XSP
        2000-01-10 open Assets:Cash
        2000-01-10 open Assets:External
        2000-01-10 open Expenses:Foreign

        2010-01-01 commodity USD

        2010-01-01 commodity QQQ
          name: "PowerShares QQQ Trust, Series 1 (ETF)"
          price: "USD:yahoo/NASDAQ:QQQ"

        2010-01-01 commodity XSP
          name: "iShares S&P 500 Index Fund (CAD Hedged)"
          quote: CAD

        2010-01-01 commodity AMTKPTS
          quote: USD
          price: ""

        """
        self.entries = entries

    def test_find_currencies_declared(self):
        currencies = price.find_currencies_declared(self.entries, None)
        currencies2 = [(base, quote) for base, quote, _ in currencies]
        self.assertEqual([('QQQ', 'USD')], currencies2)


if __name__ == '__main__':
    unittest.main()
