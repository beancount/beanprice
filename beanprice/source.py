"""Interface definition for all price sources.

This module describes the contract to be fulfilled by all implementations of
price sources.

TODO(blais): It would be an improvement if the interfaces here return an
indication of why fetching failed and leave the responsibility to the caller to
decide whether to share this with the user or to ignore and continue with other
sources.
"""

__copyright__ = "Copyright (C) 2015-2020  Martin Blais"
__license__ = "GNU GPLv2"

import datetime
from decimal import Decimal
from typing import List, Optional, NamedTuple


# A record that contains data for a price fetched from a source.
#
# A triple of
#   price: A Decimal instance, the price or rate.
#   time: A datetime.time instance at which that price or rate was available.
#     Note that this instance is REQUIRED to be timezone aware, as this is
#     used to compute a corresponding date in the user's timezone.
#   quote-currency: A string, the quote currency of the given price, if
#     available.
SourcePrice = NamedTuple(
    "SourcePrice",
    [
        ("price", Decimal),
        ("time", Optional[datetime.datetime]),
        ("quote_currency", Optional[str]),
    ],
)


class MissingDate(BaseException):
    """An attempt to read a missing date, ignore and continue"""


class Source:
    """Interface to be implemented by all price sources.

    Notes about arguments below:
      `ticker` arguments: A string, the ticker to be fetched by the source. This
        ticker may include structure, such as the exchange code. Also note that
        this ticker is source-specified, and is not necessarily the same value
        as the commodity symbol used in the Beancount file.
      time arguments: A `datetime.datetime` instance. This is a timezone-aware
        `datetime` you can convert to any timezone. For past dates we query for
        a time that is equivalent to 4pm in the user's timezone.

    About return values:
      If the price could not be fetched, None is returned and another source
      should be consulted. There is never any guarantee that a price source will
      be able to fetch its value and failure to fetch is more frequent than one
      might assume in practice; client code must be able to handle this and try
      again with another price source until all sources are exhausted.

      Also, note in the case we were able to fetch, the price's returned time
      must be timezone-aware (not naive).
    """

    def get_latest_price(self, ticker: str) -> Optional[SourcePrice]:
        """Fetch the current latest price. The date may differ.

        This routine attempts to fetch the most recent available price, and
        returns the actual date of the quoted price, which may differ from the
        date this call is made at. {1cfa25e37fc1}

        Args:
          ticker: A string, the ticker to be fetched by the source.
        Returns:
          A SourcePrice instance, or None if we failed to fetch.
        """

    def get_historical_price(
        self, ticker: str, time: datetime.datetime
    ) -> Optional[SourcePrice]:
        """Return the lastest historical price found for the symbol at the given date.

        This could be the price of the close of the day, for instance. We assume
        that there is some single price representative of the day. Also note
        that if you're querying for a weekend or holiday (closed market) date,
        the price returned may have a date earlier than the one you requested
        (the latest available market price for that instrument is from a prior
        date).

        Args:
          ticker: A string, the ticker to be fetched by the source.
          time: The timestamp at which to query for the price.
        Returns:
          A SourcePrice instance, or None if we failed to fetch.
        """

    def get_prices_series(
        self, ticker: str, time_begin: datetime.datetime, time_end: datetime.datetime
    ) -> Optional[List[SourcePrice]]:
        """Return the historical daily price series between two dates.

        Note that weekends don't have any prices, so there's no guarantee that
        this returns a contiguous series of prices for each day in the requested
        interval.

        Args:
          ticker: A string, the ticker to be fetched by the source.
          time_begin: The earliest timestamp whose prices to include.
          time_end: The latest timestamp whose prices to include.
        Returns:
          A list of SourcePrice instances, sorted by date/time, or None if we
          failed to fetch. An empty list signals success fetching but no data in
          the requested interval.
        """
