"""Validated, atomic end-of-day valuation for the assets actually held.

Unlike bean-price, this command requires complete coverage before writing. Native
quotes and dated FX rates are retained alongside converted operating-currency
prices. It never changes transaction costs or broker settlement amounts.
"""

import argparse
import calendar
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, localcontext
import os
from pathlib import Path
import sys
import tempfile

from beancount import loader
from beancount.core import amount, data
from beancount.ops import validation
from beancount.parser import parser, printer
from beanprice.price import parse_source_map
from beanprice.source import Source

LOCAL_TIMEZONE = timezone(timedelta(hours=8))


class SyncError(ValueError):
    """The proposed update cannot be safely written."""


def held_commodities(entries, asof, currency):
    """Include nonzero asset positions at the end of the requested day.

    Keep account balances separate: a long in one account must not conceal a
    short in another. Cash in foreign currencies also needs valuation.
    """
    balances = defaultdict(Decimal)
    for entry in entries:
        if isinstance(entry, data.Transaction) and entry.date <= asof:
            for posting in entry.postings:
                if posting.account.startswith("Assets:"):
                    balances[posting.account, posting.units.currency] += posting.units.number
    return {symbol for (_, symbol), number in balances.items()
            if number and symbol != currency}


def check_quote(quote, expected, asof, max_age):
    """Require an explicit currency, positive value and trustworthy daily date."""
    if quote is None or not isinstance(quote.price, Decimal):
        raise SyncError("No decimal price returned")
    if not quote.price.is_finite() or quote.price <= 0:
        raise SyncError("Non-positive or non-finite price")
    if quote.quote_currency != expected:
        raise SyncError(f"Currency mismatch: expected {expected}, got {quote.quote_currency}")
    if quote.time is None or quote.time.utcoffset() is None:
        raise SyncError("Missing or timezone-naive quote timestamp")
    observed = quote.time.astimezone(LOCAL_TIMEZONE).date()
    age = (asof - observed).days
    if age < 0 or age > max_age:
        raise SyncError(f"Quote date {observed} outside {asof} minus {max_age} days")
    return observed


def fetch_quote(spec, asof, max_age):
    """Try explicitly configured alternatives, validating each before accepting."""
    mapping = parse_source_map(spec)
    if len(mapping) != 1:
        raise SyncError("Configure one native quote currency per commodity")
    currency, sources = next(iter(mapping.items()))
    failures = []
    for item in sources:
        name = f"{item.module.__name__}/{item.symbol}"
        try:
            if item.invert:
                raise SyncError("Use an explicit BASE-QUOTE FX source, not inversion")
            provider = item.module.Source()
            end_time = datetime.combine(asof, time(23, 59), LOCAL_TIMEZONE)
            # A relaxed age limit must also expand providers' usual ten-day window.
            if max_age > 10 and type(provider).get_prices_series is not Source.get_prices_series:
                series = provider.get_prices_series(
                    item.symbol, end_time - timedelta(days=max_age), end_time)
                candidates = []
                for value in series or []:
                    observed = check_quote(value, currency, asof, max_age)
                    candidates.append((observed, value))
                if not candidates:
                    raise SyncError("No price in the extended date range")
                quote = max(candidates, key=lambda value: value[0])[1]
            else:
                quote = provider.get_historical_price(item.symbol, end_time)
            observed = check_quote(quote, currency, asof, max_age)
            return quote, observed, name
        except Exception as exc:
            failures.append(f"{name}: {type(exc).__name__}: {str(exc)[:240]}")
    raise SyncError("; ".join(failures) or "No price source configured")


def price_entry(symbol, value, currency, observed, provenance):
    meta = data.new_metadata("<price-sync>", 0)
    meta.update(provenance)
    return data.Price(meta, observed, symbol, amount.Amount(value, currency))


def collect_prices(entries, dates, currency="CNY", max_age=7, fetch=fetch_quote):
    """Fetch a complete batch in memory, collecting failures across holdings."""
    result, failures, cache = [], [], {}

    def fetch_cached(spec, asof):
        key = spec, asof
        if key not in cache:
            cache[key] = fetch(spec, asof, max_age)
        return cache[key]

    for asof in sorted(set(dates)):
        declarations = {entry.currency: entry.meta for entry in entries
                        if isinstance(entry, data.Commodity) and entry.date <= asof}
        for symbol in sorted(held_commodities(entries, asof, currency)):
            try:
                spec = declarations.get(symbol, {}).get("price")
                if not spec:
                    raise SyncError("Missing commodity price configuration")
                quote, observed, source = fetch_cached(spec, asof)
                result.append(price_entry(symbol, quote.price, quote.quote_currency,
                                          observed, {"source": source}))
                if quote.quote_currency == currency:
                    continue
                fx_spec = declarations.get(quote.quote_currency, {}).get("price")
                if not fx_spec:
                    raise SyncError(f"Missing FX configuration for {quote.quote_currency}")
                fx, fx_date, fx_source = fetch_cached(fx_spec, observed)
                check_quote(fx, currency, observed, max_age)
                result.append(price_entry(quote.quote_currency, fx.price, currency,
                                          fx_date, {"source": fx_source}))
                with localcontext() as context:
                    context.prec = 28
                    converted = (quote.price * fx.price).quantize(Decimal("0.00000001"))
                if converted <= 0:
                    raise SyncError("Converted price rounds to zero")
                result.append(price_entry(symbol, converted, currency, observed, {
                    "source": "beanprice.sync", "native-currency": quote.quote_currency,
                    "native-price": quote.price, "native-source": source,
                    "fx-rate": fx.price, "fx-date": fx_date, "fx-source": fx_source,
                }))
            except Exception as exc:
                failures.append(f"{asof} {symbol}: {exc}")
    if failures:
        raise SyncError("No prices written:\n" + "\n".join(failures))
    return result


def merge_prices(original, proposed):
    """Preserve original text, append new keys, and refuse conflicting values."""
    existing, errors, _ = parser.parse_string(original)
    if errors or any(not isinstance(entry, data.Price) for entry in existing):
        raise SyncError("Output must be a valid price-only Beancount file")
    index = defaultdict(set)
    for entry in existing:
        index[entry.date, entry.currency, entry.amount.currency].add(entry.amount.number)
    additions = []
    for entry in sorted(proposed, key=lambda p: (p.date, p.currency, p.amount.currency)):
        key = entry.date, entry.currency, entry.amount.currency
        if key in index:
            if index[key] != {entry.amount.number}:
                raise SyncError(f"Conflicting price for {key}; review manually")
            continue
        index[key].add(entry.amount.number)
        additions.append(entry)
    if not additions:
        return original, []
    text = original.rstrip() + "\n\n; Validated end-of-day price sync\n"
    text += "\n".join(printer.format_entry(entry) for entry in additions) + "\n"
    text = text.rstrip() + "\n"
    _, errors, _ = parser.parse_string(text)
    if errors:
        raise SyncError(f"Generated price syntax invalid: {errors}")
    return text, additions


def sync(ledger, output, dates, currency="CNY", max_age=7, dry_run=False,
         fetch=fetch_quote):
    """Validate before replacement; lock concurrent syncs and check input changes."""
    ledger, output = Path(ledger).resolve(), Path(output).resolve()
    lock = output.with_name(output.name + ".sync.lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise SyncError(f"Another sync holds {lock}; inspect before removing a stale lock") from exc
    os.close(descriptor)
    temporary = None
    try:
        entries, errors, options = loader.load_file(str(ledger))
        if errors:
            raise SyncError(f"Ledger has {len(errors)} errors; run bean-check first")
        included = {Path(path).resolve() for path in options["include"]}
        if output not in included:
            raise SyncError("Output file must already be included by the ledger")
        snapshots = {path: path.read_bytes() for path in included}
        original = snapshots[output].decode("utf-8-sig")
        proposed = collect_prices(entries, dates, currency, max_age, fetch)
        rendered, additions = merge_prices(original, proposed)
        errors = validation.validate(sorted(entries + additions, key=data.entry_sortkey), options)
        if errors:
            raise SyncError(f"Updated ledger validation failed: {errors}")
        if dry_run or not additions:
            return additions
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=output.parent, prefix=".price-sync-",
                                         suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(rendered)
            stream.flush()
            os.fsync(stream.fileno())
        if any(path.read_bytes() != content for path, content in snapshots.items()):
            raise SyncError("Ledger changed during sync; retry against the new contents")
        os.replace(temporary, output)
        temporary = None
        return additions
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)


def month_ends(begin, end):
    """Yield month ends in an inclusive calendar range."""
    current = begin.replace(day=1)
    while current <= end:
        last = current.replace(day=calendar.monthrange(current.year, current.month)[1])
        if begin <= last <= end:
            yield last
        current = last + timedelta(days=1)


def main(argv=None):
    args_parser = argparse.ArgumentParser(description=__doc__)
    args_parser.add_argument("ledger", type=Path)
    args_parser.add_argument("--output", type=Path, required=True)
    args_parser.add_argument("--currency", default="CNY")
    args_parser.add_argument("--date", type=date.fromisoformat, action="append")
    args_parser.add_argument("--month-ends", type=date.fromisoformat, nargs=2,
                             metavar=("BEGIN", "END"))
    args_parser.add_argument("--max-age", type=int, default=7,
                             help="Maximum quote/FX age in calendar days (default 7)")
    args_parser.add_argument("--dry-run", action="store_true")
    args = args_parser.parse_args(argv)
    today = datetime.now(LOCAL_TIMEZONE).date()
    dates = args.date or []
    if args.month_ends:
        dates.extend(month_ends(*args.month_ends))
    if not dates:
        if args.month_ends:
            args_parser.error("Requested range contains no month ends")
        dates = [today - timedelta(days=1)]
    if args.max_age < 0 or any(day >= today for day in dates):
        args_parser.error("Use completed dates before today and a nonnegative max-age")
    print(f"Fetching complete holdings for {len(set(dates))} date(s)...",
          file=sys.stderr, flush=True)
    try:
        additions = sync(args.ledger, args.output, dates, args.currency,
                         args.max_age, args.dry_run)
    except (SyncError, OSError, ValueError) as exc:
        print(f"Price sync failed: {exc}", file=sys.stderr)
        return 1
    for entry in additions:
        print(f"{entry.date} {entry.currency}: {entry.amount}")
    action = "Would add" if args.dry_run else "Added"
    print(f"{action} {len(additions)} price records; all held commodities covered.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
