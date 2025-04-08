"""Driver code for the price script."""

__copyright__ = "Copyright (C) 2015-2020  Martin Blais"
__license__ = "GNU GPLv2"

import argparse
import collections
import datetime
import functools
from os import path
import shelve
import tempfile
import hashlib
import re
import sys
import logging
from concurrent import futures
from typing import Any, Dict, List, Optional, NamedTuple, Tuple

from dateutil import tz

from beancount.core.number import ONE
from beancount import loader
from beancount.core import data
from beancount.core import amount
from beancount.core import prices
from beancount.core import getters
from beancount.ops import lifetimes
from beancount.parser import printer
from beancount.ops import find_prices

from beanprice import date_utils
from beanprice.source import MissingDate
import beanprice


# A price source.
#
#   module: A Python module, the module to be called to create a price source.
#   symbol: A ticker symbol in the universe of the source.
#   invert: A boolean, true if we need to invert the currency.
class PriceSource(NamedTuple):
    module: Any
    symbol: str
    invert: bool


# A dated price source description.
#
# Attributes:
#   base: A commodity string, the base for the given symbol from the input file.
#     This may be null if we don't have a mapping for it.
#   quote: A commodity string, the quote currency that defines the units of the price.
#     This is also intended to be a commodity from the input file, and similarly,
#     may be null.
#   date: A datetime.date object for the date to be fetched, or None
#     with the meaning of fetching the latest price.
#   sources: A list of PriceSource instances describing where to fetch prices from.
class DatedPrice(NamedTuple):
    base: Optional[str]
    quote: Optional[str]
    date: Optional[datetime.date]
    sources: List[PriceSource]


# The Python package where the default sources are found.
DEFAULT_PACKAGE = "beanprice.sources"


# Stand-in currency name for unknown currencies.
UNKNOWN_CURRENCY = "?"


# A cache for the prices.
_CACHE = None

# Expiration for latest prices in the cache.
DEFAULT_EXPIRATION = datetime.timedelta(seconds=30 * 60)  # 30 mins.


# The default source parser is back.
DEFAULT_SOURCE = "beanprice.sources.yahoo"


def format_dated_price_str(dprice: DatedPrice) -> str:
    """Convert a dated price to a one-line printable string.

    Args:
      dprice: A DatedPrice instance.
    Returns:
      The string for a DatedPrice instance.
    """
    psstrs = [
        "{}({}{})".format(
            psource.module.__name__, "1/" if psource.invert else "", psource.symbol
        )
        for psource in dprice.sources
    ]
    base_quote = "{} /{}".format(dprice.base, dprice.quote)
    return "{:<32} @ {:10} [ {} ]".format(
        base_quote, dprice.date.isoformat() if dprice.date else "latest", ",".join(psstrs)
    )


def parse_source_map(source_map_spec: str) -> Dict[str, List[PriceSource]]:
    """Parse a source map specification string.

    Source map specifications allow the specification of multiple sources for
    multiple quote currencies and follow the following syntax:

       <currency1>:<source1>,<source2>,... <currency2>:<source1>,...

    Where a <source> itself follows:

       <module>/[^]<ticker>

    The <module> is resolved against the Python path, but first looked up under
    the package where the default price extractors lie. The presence of a '^'
    character indicates that we should use the inverse of the rate pull from
    this source.

    For example, for prices of AAPL in USD:

       USD:google/NASDAQ:AAPL,yahoo/AAPL

    Or for the exchange rate of a currency, such as INR in USD or in CAD:

       USD:google/^CURRENCY:USDINR CAD:google/^CURRENCY:CADINR

    Args:
      source_map_spec: A string, a full source map specification to be parsed.
    Returns:
      A dict of quote currency to price sources for that currency.
    Raises:
      ValueError: If an invalid pattern has been specified.
    """
    source_map: Dict[str, List[PriceSource]] = collections.defaultdict(list)
    for source_list_spec in re.split("[ ;]", source_map_spec):
        match = re.match("({}):(.*)$".format(amount.CURRENCY_RE), source_list_spec)
        if not match:
            raise ValueError('Invalid source map pattern: "{}"'.format(source_list_spec))

        currency, source_strs = match.groups()
        source_map[currency].extend(
            parse_single_source(source_str) for source_str in source_strs.split(",")
        )
    return source_map


def parse_single_source(source: str) -> PriceSource:
    """Parse a single source string.

    Source specifications follow the syntax:

      <module>/[^]<ticker>

    The <module> is resolved against the Python path, but first looked up
    under the package where the default price extractors lie.

    Args:
      source: A single source string specification.
    Returns:
      A PriceSource tuple.
    Raises:
      ValueError: If invalid.
    """
    match = re.match(r"([a-zA-Z]+[a-zA-Z0-9\._]+)/(\^?)([a-zA-Z0-9:=_\-\.\(\)]+)$", source)
    if not match:
        raise ValueError('Invalid source name: "{}"'.format(source))
    short_module_name, invert, symbol = match.groups()
    module = import_source(short_module_name)
    return PriceSource(module, symbol, bool(invert))


def import_source(module_name: str):
    """Import the source module defined by the given name.

    The default location is handled here.

    Args:
      short_module_name: A string, the name of a Python module, which may
        be within the default package or a full name.
    Returns:
      A corresponding Python module object.
    Raises:
      ImportError: If the module cannot be imported.
    """
    default_name = "{}.{}".format(DEFAULT_PACKAGE, module_name)
    try:
        __import__(default_name)
        return sys.modules[default_name]
    except ImportError:
        try:
            __import__(module_name)
            return sys.modules[module_name]
        except ImportError as exc:
            raise ImportError(
                'Could not find price source module "{}"'.format(module_name)
            ) from exc


def find_currencies_declared(
    entries: data.Entries,
    date: Optional[datetime.date] = None,
) -> List[Tuple[str, str, List[PriceSource]]]:
    """Return currencies declared in Commodity directives.

    If a 'price' metadata field is provided, include all the quote currencies
    there-in. Otherwise, the Commodity directive is ignored.

    Args:
      entries: A list of directives.
      date: A datetime.date instance.
    Returns:
      A list of (base, quote, list of PriceSource) currencies. The list of
      (base, quote) pairs is guaranteed to be unique.
    """
    currencies = []
    for entry in entries:
        if not isinstance(entry, data.Commodity):
            continue
        if date and entry.date >= date:
            break

        # Here we have to infer which quote currencies the commodity is for
        # (maybe down the road this should be better handled by providing a list
        # of quote currencies in the Commodity directive itself).
        #
        # First, we look for a "price" metadata field, which defines conversions
        # for various currencies. Each of these quote currencies generates a
        # pair in the output.
        source_str = entry.meta.get("price", None)
        if source_str is not None:
            if source_str == "":
                logging.debug(
                    "Skipping ignored currency (with empty price): %s", entry.currency
                )
                continue
            try:
                source_map = parse_source_map(source_str)
            except ValueError as exc:
                logging.warning(
                    "Ignoring currency with invalid 'price' source: %s (%s)",
                    entry.currency,
                    exc,
                )
            else:
                for quote, psources in source_map.items():
                    currencies.append((entry.currency, quote, psources))
        else:
            # Otherwise we simply ignore the declaration. That is, a Commodity
            # directive without any "price" metadata would not register as a
            # declared currency.
            logging.debug("Ignoring currency with no metadata: %s", entry.currency)

    return currencies


def log_currency_list(message, currencies):
    """Log a list of currencies to debug output.

    Args:
      message: A message string to prepend.
      currencies: A list of (base, quote) currency pair.
    """
    logging.debug("-------- {}:".format(message))
    for base, quote in currencies:
        logging.debug("  {:>32}".format("{} /{}".format(base, quote)))


def get_price_jobs_at_date(
    entries: data.Entries,
    date: Optional[datetime.date] = None,
    inactive: bool = False,
    undeclared_source: Optional[str] = None,
):
    """Get a list of prices to fetch from a stream of entries.

    The active holdings held on the given date are included.

    Args:
      entries: A list of beancount entries, the name of a file to process.
      date: A datetime.date instance.
      inactive: Include currencies with no balance at the given date. The default
        is to only include those currencies which have a non-zero balance.
      undeclared_source: A string, the name of the default source module to use to
        pull prices for commodities without a price source metadata on their
        Commodity directive declaration.
    Returns:
      A list of DatedPrice instances.

    """
    # Find the list of declared currencies, and from it build a mapping for
    # tickers for each (base, quote) pair. This is the only place tickers
    # appear.
    declared_triples = find_currencies_declared(entries, date)
    currency_map = {(base, quote): psources for base, quote, psources in declared_triples}

    # Compute the initial list of currencies to consider.
    if undeclared_source:
        # Use the full set of possible currencies.
        cur_at_cost = find_prices.find_currencies_at_cost(entries)
        cur_converted = find_prices.find_currencies_converted(entries, date)
        cur_priced = find_prices.find_currencies_priced(entries, date)
        currencies = cur_at_cost | cur_converted | cur_priced
        log_currency_list("Currency held at cost", cur_at_cost)
        log_currency_list("Currency converted", cur_converted)
        log_currency_list("Currency priced", cur_priced)
        default_source = import_source(undeclared_source)
    else:
        # Use the currencies from the Commodity directives.
        currencies = set(currency_map.keys())
        default_source = None

    log_currency_list("Currencies in primary list", currencies)

    # By default, restrict to only the currencies with non-zero balances at the
    # given date.
    if not inactive:
        balance_currencies = find_prices.find_balance_currencies(entries, date)
        log_currency_list("Currencies held in assets", balance_currencies)
        currencies = currencies & balance_currencies

    log_currency_list("Currencies to fetch", currencies)

    # Build up the list of jobs to fetch prices for.
    jobs = []
    for base_quote in currencies:
        psources = currency_map.get(base_quote, None)
        base, quote = base_quote

        # If there are no sources, create a default one.
        if not psources:
            psources = [PriceSource(default_source, base, False)]

        jobs.append(DatedPrice(base, quote, date, psources))
    return sorted(jobs)


# TODO(blais): This could be modified to use the get_daily_prices() interface,
# or perhaps to extend it to intervals, and let the price source decide for
# itself how to implement fetching (e.g., use a single call + filter, or use
# multiple calls). Querying independently for each day is not the best strategy.
def get_price_jobs_up_to_date(
    entries,
    date_last=None,
    inactive=False,
    undeclared_source=None,
    update_rate="weekday",
    compress_days=1,
):
    """Get a list of trailing prices to fetch from a stream of entries.

    The list of dates runs from the latest available price up to the latest date.

    Args:
      entries: list of Beancount entries
      date_last: The date up to where to find prices to as an exclusive range end.
      inactive: Include currencies with no balance at the given date. The default
        is to only include those currencies which have a non-zero balance.
      undeclared_source: A string, the name of the default source module to use to
        pull prices for commodities without a price source metadata on their
        Commodity directive declaration.
    Returns:
      A list of DatedPrice instances.
    """
    price_map = prices.build_price_map(entries)

    # Find the list of declared currencies, and from it build a mapping for
    # tickers for each (base, quote) pair. This is the only place tickers
    # appear.
    declared_triples = find_currencies_declared(entries, date_last)
    currency_map = {(base, quote): psources for base, quote, psources in declared_triples}

    # Compute the initial list of currencies to consider.
    if undeclared_source:
        # Use the full set of possible currencies.
        cur_at_cost = find_prices.find_currencies_at_cost(entries)
        cur_converted = find_prices.find_currencies_converted(entries, date_last)
        cur_priced = find_prices.find_currencies_priced(entries, date_last)
        currencies = cur_at_cost | cur_converted | cur_priced
        log_currency_list("Currency held at cost", cur_at_cost)
        log_currency_list("Currency converted", cur_converted)
        log_currency_list("Currency priced", cur_priced)
        default_source = import_source(undeclared_source)
    else:
        # Use the currencies from the Commodity directives.
        currencies = set(currency_map.keys())
        default_source = None

    log_currency_list("Currencies in primary list", currencies)

    # By default, restrict to only the currencies with non-zero balances
    # up to the given date.
    # Also, find the earliest start date to fetch prices from.
    # Look at both latest prices and start dates.
    lifetimes_map = lifetimes.get_commodity_lifetimes(entries)
    commodity_map = getters.get_commodity_directives(entries)

    if inactive:
        for base_quote in currencies:
            if lifetimes_map[base_quote]:
                # Use first date from lifetime
                lifetimes_map[base_quote] = [(lifetimes_map[base_quote][0][0], None)]
            else:
                # Insert never active commodities into lifetimes
                # Start from date of currency directive
                base, _ = base_quote
                commodity_entry = commodity_map.get(base, None)
                lifetimes_map[base_quote] = [(commodity_entry.date, None)]
    else:
        # Compress any lifetimes based on compress_days
        lifetimes_map = lifetimes.compress_lifetimes_days(lifetimes_map, compress_days)

    # Trim lifetimes based on latest price dates.
    for base_quote in lifetimes_map:
        intervals = lifetimes_map[base_quote]
        result = prices.get_latest_price(price_map, base_quote)
        if result is None or result[0] is None:
            lifetimes_map[base_quote] = lifetimes.trim_intervals(intervals, None, date_last)
        else:
            latest_price_date = result[0]
            date_first = latest_price_date + datetime.timedelta(days=1)
            if date_first < date_last:
                lifetimes_map[base_quote] = lifetimes.trim_intervals(
                    intervals, date_first, date_last
                )
            else:
                # We don't need to update if we're already up to date.
                lifetimes_map[base_quote] = []

    # Remove currency pairs we can't fetch any prices for.
    if not default_source:
        keys = list(lifetimes_map.keys())
        for key in keys:
            if not currency_map.get(key, None):
                del lifetimes_map[key]

    # Create price jobs based on fetch rate
    if update_rate == "daily":
        required_prices = lifetimes.required_daily_prices(
            lifetimes_map, date_last, weekdays_only=False
        )
    elif update_rate == "weekday":
        required_prices = lifetimes.required_daily_prices(
            lifetimes_map, date_last, weekdays_only=True
        )
    elif update_rate == "weekly":
        required_prices = lifetimes.required_weekly_prices(lifetimes_map, date_last)
    else:
        raise ValueError("Invalid Update Rate")

    jobs = []
    # Build up the list of jobs to fetch prices for.
    for key in required_prices:
        date, base, quote = key
        psources = currency_map.get((base, quote), None)
        if not psources:
            psources = [PriceSource(default_source, base, False)]

        jobs.append(DatedPrice(base, quote, date, psources))

    return sorted(jobs)


def now():
    "Indirection in order to be able to mock it out in the tests."
    return datetime.datetime.now(datetime.timezone.utc)


def fetch_cached_price(source, symbol, date):
    """Call Source to fetch a price, but look and/or update the cache first.

    This function entirely deals with caching and correct expiration. It keeps
    old prices if they were fetched in the past, and it quickly expires
    intra-day prices if they are fetched on the same day.

    Args:
      source: A Python module object.
      symbol: A string, the ticker to fetch.
      date: A datetime.date instance, None if we're to fetch the latest date.
    Returns:
      A SourcePrice instance.
    """
    # Compute a suitable timestamp from the date, if specified.
    if date is not None:
        # We query as for 4pm for the given date of the current timezone, if
        # specified.
        query_time = datetime.time(16, 0, 0)
        time_local = datetime.datetime.combine(date, query_time, tzinfo=tz.tzlocal())
        time = time_local.astimezone(tz.tzutc())
    else:
        time = None

    if _CACHE is None:
        # The cache is disabled; just call and return.
        result = (
            source.get_latest_price(symbol)
            if time is None
            else source.get_historical_price(symbol, time)
        )

    else:
        # The cache is enabled and we have to compute the current/latest price.
        # Try to fetch from the cache but miss if the price is too old.
        md5 = hashlib.md5()
        md5.update(str((type(source).__module__, symbol, date)).encode("utf-8"))
        key = md5.hexdigest()
        timestamp_now = int(now().timestamp())
        try:
            timestamp_created, result_naive = _CACHE[key]

            # Convert naive timezone to UTC, which is what the cache is always
            # assumed to store. (The reason for this is that timezones from
            # aware datetime objects cannot be serialized properly due to bug.)
            if result_naive.time is not None:
                result = result_naive._replace(
                    time=result_naive.time.replace(tzinfo=tz.tzutc())
                )
            else:
                result = result_naive

            if (timestamp_now - timestamp_created) > _CACHE.expiration.total_seconds():
                raise KeyError
        except KeyError:
            logging.info("Fetching: %s (time: %s)", symbol, time)
            try:
                result = (
                    source.get_latest_price(symbol)
                    if time is None
                    else source.get_historical_price(symbol, time)
                )
            except ValueError as exc:
                logging.error("Error fetching %s: %s", symbol, exc)
                result = None

            # Make sure the timezone is UTC and make naive before serialization.
            if result and result.time is not None:
                time_utc = result.time.astimezone(tz.tzutc())
                time_naive = time_utc.replace(tzinfo=None)
                result_naive = result._replace(time=time_naive)
            else:
                result_naive = result

            if result_naive is not None:
                _CACHE[key] = (timestamp_now, result_naive)
    return result


def setup_cache(cache_filename: Optional[str], clear_cache: bool):
    """Setup the results cache.

    Args:
      cache_filename: A string or None, the base filename for the cache. An extension
        may be added to the filename and more than one file may be created.
      clear_cache: A boolean, if true, delete the cache before beginning.
    """
    if not cache_filename:
        return

    logging.info('Using price cache at "%s" (with indefinite expiration)', cache_filename)

    flag = "c"
    if clear_cache and cache_filename:
        logging.info("Clearing cache %s*", cache_filename)
        flag = "n"

    global _CACHE
    _CACHE = shelve.open(cache_filename, flag=flag)  # type: ignore
    _CACHE.expiration = DEFAULT_EXPIRATION  # type: ignore


def reset_cache():
    """Reset the cache to its uninitialized state."""
    global _CACHE
    if _CACHE is not None:
        _CACHE.close()
    _CACHE = None


def fetch_price(dprice: DatedPrice, swap_inverted: bool = False) -> Optional[data.Price]:
    """Fetch a price for the DatedPrice job.

    Args:
      dprice: A DatedPrice instances.
      swap_inverted: A boolean, true if we should invert currencies instead of
        rate for an inverted price source.
    Returns:
      A Price entry corresponding to the output of the jobs processed.

    """
    for psource in dprice.sources:
        try:
            source = psource.module.Source()
        except AttributeError:
            continue
        try:
            srcprice = fetch_cached_price(source, psource.symbol, dprice.date)
        except MissingDate:
            logging.debug("Missing date {} for symbol {}".format(dprice.date, psource.symbol))
            return None
        if srcprice is not None:
            break
    else:
        if dprice.sources:
            logging.error("Could not fetch for job: %s", dprice)
        return None

    base = dprice.base
    quote = dprice.quote or srcprice.quote_currency
    price = srcprice.price

    # Invert the rate if requested.
    if psource.invert:
        if swap_inverted:
            base, quote = quote, base
        else:
            price = ONE / price

    assert base is not None
    fileloc = data.new_metadata("<{}>".format(type(psource.module).__name__), 0)

    # The datetime instance is required to be aware. We always convert to the
    # user's timezone before extracting the date. This means that if the market
    # returns a timestamp for a particular date, once we convert to the user's
    # timezone the returned date may be different by a day. The intent is that
    # whatever we print is assumed coherent with the user's timezone. See
    # discussion at
    # https://groups.google.com/d/msg/beancount/9j1E_HLEMBQ/fYRuCQK_BwAJ
    srctime = srcprice.time
    if srctime.tzinfo is None:
        raise ValueError("Time returned by the price source is not timezone aware.")
    date = srctime.astimezone(tz.tzlocal()).date()

    return data.Price(fileloc, date, base, amount.Amount(price, quote or UNKNOWN_CURRENCY))


def filter_redundant_prices(
    price_entries: List[data.Price], existing_entries: List[data.Price], diffs: bool = False
) -> Tuple[List[data.Price], List[data.Price]]:
    """Filter out new entries that are redundant from an existing set.

    If the price differs, we override it with the new entry only on demand. This
    is because this would create conflict with existing price entries when
    parsing, if the new entries are simply inserted into the input.

    Args:
      price_entries: A list of newly created, proposed to be added Price directives.
      existing_entries: A list of existing entries we are proposing to add to.
      diffs: A boolean, true if we should output differing price entries
        at the same date.
    Returns:
      A filtered list of remaining entries, and a list of ignored entries.
    """
    # Note: We have to be careful with the dates, because requesting the latest
    # price for a date may yield the price at a previous date. Clobber needs to
    # take this into account. See {1cfa25e37fc1}.
    existing_prices = {
        (entry.date, entry.currency): entry
        for entry in existing_entries
        if isinstance(entry, data.Price)
    }
    filtered_prices: List[data.Price] = []
    ignored_prices: List[data.Price] = []
    for entry in price_entries:
        key = (entry.date, entry.currency)
        if key in existing_prices:
            if diffs:
                existing_entry = existing_prices[key]
                if existing_entry.amount == entry.amount:
                    output = ignored_prices
            else:
                output = ignored_prices
        else:
            output = filtered_prices
        output.append(entry)
    return filtered_prices, ignored_prices


def process_args() -> Tuple[
    argparse.Namespace,
    List[DatedPrice],
    data.Directives,
    Optional[Any],
]:
    """Process the arguments. This also initializes the logging module.

    Returns:
      A tuple of:
        args: The argparse receiver of command-line arguments.
        jobs: A list of DatedPrice job objects.
        entries: A list of all the parsed entries.
        dcontext: A context used to determine decimal precision when printing.
    """
    parser = argparse.ArgumentParser(description=beanprice.__doc__.splitlines()[0])

    # Input sources or filenames.
    parser.add_argument(
        "sources",
        nargs="+",
        help=(
            'A list of filenames (or source "module/symbol", if -e is '
            "specified) from which to create a list of jobs."
        ),
    )

    parser.add_argument(
        "-e",
        "--expressions",
        "--expression",
        action="store_true",
        help=('Interpret the arguments as "module/symbol" source strings.'),
    )

    # Regular options.
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        help=("Print out progress log. Specify twice for debugging info."),
    )

    parser.add_argument(
        "-d",
        "--date",
        action="store",
        type=date_utils.parse_date_liberally,
        help=("Specify the date for which to fetch the prices."),
    )

    parser.add_argument(
        "--update",
        action="store_true",
        help=(
            "Fetch prices from most recent price for each source "
            "up to present day or specified --date. See also "
            "--update-rate, --update-compress options."
        ),
    )

    parser.add_argument(
        "--update-rate",
        choices=["daily", "weekday", "weekly"],
        default="weekday",
        help=(
            "Specify how often dates are fetched. Options are daily, weekday, or weekly "
            "(fridays)"
        ),
    )

    parser.add_argument(
        "--update-compress",
        action="store",
        type=int,
        default=0,
        help=(
            "Specify the number of inactive days to ignore. This option ignored if "
            "--inactive used."
        ),
    )

    parser.add_argument(
        "-i",
        "--inactive",
        action="store_true",
        help=(
            "Select all commodities from input files, not just the ones active on the date"
        ),
    )

    parser.add_argument(
        "-u",
        "--undeclared",
        action="store_true",
        help=(
            "Include commodities viewed in the file even without a "
            "corresponding Commodity directive, from this default source. "
            "The currency name itself is used as the lookup symbol in this default source."
        ),
    )

    parser.add_argument(
        "-c",
        "--clobber",
        action="store_true",
        help=(
            "Do not skip prices which are already present in input files; "
            "fetch them anyway."
        ),
    )

    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help=("A shorthand for --inactive, --undeclared, --clobber."),
    )

    parser.add_argument(
        "-s",
        "--swap-inverted",
        action="store_true",
        help=(
            "For inverted sources, swap currencies instead of inverting the rate. "
            "For example, if fetching the rate for CAD from 'USD:google/^CURRENCY:USDCAD' "
            'results in 1.25, by default we would output "price CAD  0.8000 USD". '
            'Using this option we would instead output " price USD   1.2500 CAD".'
        ),
    )

    parser.add_argument(
        "-w",
        "--workers",
        action="store",
        type=int,
        default=1,
        help=("Specify the number of concurrent fetchers."),
    )

    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help=(
            "Don't actually fetch the prices, just print the list of the ones "
            "to be fetched."
        ),
    )

    # Caching options.
    cache_group = parser.add_argument_group("cache")
    cache_filename = path.join(
        tempfile.gettempdir(), "{}.cache".format(path.basename(sys.argv[0]))
    )
    cache_group.add_argument(
        "--cache",
        dest="cache_filename",
        action="store",
        default=cache_filename,
        help="The base filename for the underlying price cache "
        "database. An extension may be added to the filename and "
        "more than one file may be created.",
    )
    cache_group.add_argument(
        "--no-cache",
        dest="cache_filename",
        action="store_const",
        const=None,
        help="Disable the price cache.",
    )
    cache_group.add_argument(
        "--clear-cache", action="store_true", help="Clear the cache prior to startup."
    )

    args = parser.parse_args()

    verbose_levels = {
        None: logging.WARN,
        0: logging.WARN,
        1: logging.INFO,
        2: logging.DEBUG,
    }
    logging.basicConfig(
        level=verbose_levels[args.verbose], format="%(levelname)-8s: %(message)s"
    )

    if args.undeclared:
        args.undeclared = DEFAULT_SOURCE

    if args.all:
        args.inactive = args.clobber = True
        args.undeclared = DEFAULT_SOURCE

    # Setup for processing.
    setup_cache(args.cache_filename, args.clear_cache)

    # Get the list of DatedPrice jobs to get from the arguments.
    dates = [args.date or None]
    logging.info("Processing at date: %s", args.date or datetime.date.today())

    jobs = []
    all_entries = []
    dcontext = None
    if args.expressions:
        # Interpret the arguments as price sources.
        for source_str in args.sources:
            psources: List[PriceSource] = []
            try:
                psource_map = parse_source_map(source_str)
            except ValueError:
                extra = "; did you provide a filename?" if path.exists(source_str) else ""
                msg = (
                    'Invalid source "{{}}"{}. '.format(extra)
                    + 'Supported format is "CCY:module/SYMBOL"'
                )
                parser.error(msg.format(source_str))
            else:
                for currency, psources in psource_map.items():
                    for date in dates:
                        jobs.append(
                            DatedPrice(psources[0].symbol, currency, date, psources)
                        )
    elif args.update:
        # Use Beancount input filename sources to create
        # prices jobs up to present time.
        for filename in args.sources:
            if not path.exists(filename) or not path.isfile(filename):
                parser.error(
                    'File does not exist: "{}"; ' "did you mean to use -e?".format(filename)
                )
                continue
            logging.info('Loading "%s"', filename)
            entries, errors, options_map = loader.load_file(filename, log_errors=sys.stderr)
            if dcontext is None:
                dcontext = options_map["dcontext"]
            if args.date is None:
                latest_date = datetime.date.today()
            else:
                latest_date = args.date
            jobs.extend(
                get_price_jobs_up_to_date(
                    entries,
                    latest_date,
                    args.inactive,
                    args.undeclared,
                    args.update_rate,
                    args.update_compress,
                )
            )
            all_entries.extend(entries)
    else:
        # Interpret the arguments as Beancount input filenames.
        for filename in args.sources:
            if not path.exists(filename) or not path.isfile(filename):
                parser.error(
                    'File does not exist: "{}"; ' "did you mean to use -e?".format(filename)
                )
                continue
            logging.info('Loading "%s"', filename)
            entries, errors, options_map = loader.load_file(filename, log_errors=sys.stderr)
            if dcontext is None:
                dcontext = options_map["dcontext"]
            for date in dates:
                jobs.extend(
                    get_price_jobs_at_date(entries, date, args.inactive, args.undeclared)
                )
                all_entries.extend(entries)

    return args, jobs, data.sorted(all_entries), dcontext


def main():
    args, jobs, entries, dcontext = process_args()

    # If we're just being asked to list the jobs, do this here.
    if args.dry_run:
        for dprice in jobs:
            print(format_dated_price_str(dprice))
        return

    # Fetch all the required prices, processing all the jobs.
    executor = futures.ThreadPoolExecutor(max_workers=args.workers)
    price_entries = filter(
        None,
        executor.map(
            functools.partial(fetch_price, swap_inverted=args.swap_inverted), jobs
        ),
    )

    # Sort them by currency, regardless of date (the dates should be close
    # anyhow, and we tend to put them in chunks in the input files anyhow).
    price_entries = sorted(price_entries, key=lambda e: e.currency)
    if args.update:
        # Sort additionally by date, to have an output consistent
        # with single date bean-price output.
        price_entries = sorted(price_entries, key=lambda e: e.date)

    # Avoid clobber, remove redundant entries.
    if not args.clobber:
        price_entries, ignored_entries = filter_redundant_prices(price_entries, entries)
        for entry in ignored_entries:
            logging.info("Ignored to avoid clobber: %s %s", entry.date, entry.currency)

    # Print out the entries.
    printer.print_entries(price_entries, dcontext=dcontext)
