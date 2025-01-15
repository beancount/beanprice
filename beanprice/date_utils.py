"""Date utilities."""

__copyright__ = "Copyright (C) 2020  Martin Blais"
__license__ = "GNU GPLv2"

import contextlib
import os
import time

import dateutil.parser


def parse_date_liberally(string, parse_kwargs_dict=None):
    """Parse arbitrary strings to dates.

    This function is intended to support liberal inputs, so that we can use it
    in accepting user-specified dates on command-line scripts.

    Args:
      string: A string to parse.
      parse_kwargs_dict: Dict of kwargs to pass to dateutil parser.
    Returns:
      A datetime.date object.
    """
    # At the moment, rely on the most excellent dateutil.
    if parse_kwargs_dict is None:
        parse_kwargs_dict = {}
    return dateutil.parser.parse(string, **parse_kwargs_dict).date()


@contextlib.contextmanager
def intimezone(tz_value: str):
    """Temporarily reset the value of TZ.

    This is used for testing.

    Args:
      tz_value: The value of TZ to set for the duration of this context.
    Returns:
      A contextmanager in the given timezone locale.
    """
    tz_old = os.environ.get("TZ", None)
    os.environ["TZ"] = tz_value
    time.tzset()
    try:
        yield
    finally:
        if tz_old is None:
            del os.environ["TZ"]
        else:
            os.environ["TZ"] = tz_old
        time.tzset()
