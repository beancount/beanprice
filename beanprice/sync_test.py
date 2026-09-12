"""Integration tests: real ledger loading/validation, deterministic quote fixtures."""
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from beanprice import source, sync

ASOF = date(2024, 1, 5)
LEDGER = '''option "operating_currency" "CNY"
2020-01-01 open Assets:Broker
2020-01-01 open Equity:Opening
2020-01-01 commodity HK.TEST
  price: "HKD:test/TEST"
2020-01-01 commodity HKD
  price: "CNY:test/HKD-CNY"
2024-01-02 * "Buy"
  Assets:Broker 10 HK.TEST { 8 CNY }
  Equity:Opening -80 CNY
include "prices.bean"
'''


def fake_fetch(spec, asof, max_age):
    value, currency = ("10", "HKD") if spec.startswith("HKD:") else ("0.9", "CNY")
    stamp = datetime.combine(asof, datetime.min.time(), timezone.utc)
    return source.SourcePrice(Decimal(value), stamp, currency), asof, spec


@pytest.fixture
def ledger(tmp_path):
    main, prices = tmp_path / "main.bean", tmp_path / "prices.bean"
    main.write_text(LEDGER, encoding="utf-8")
    prices.write_text("; preserve my comments\n", encoding="utf-8")
    return main, prices


def test_native_fx_and_converted_prices_are_idempotent(ledger):
    main, prices = ledger
    additions = sync.sync(main, prices, [ASOF], fetch=fake_fetch)
    assert len(additions) == 3
    original = prices.read_bytes()
    assert b"9.00000000 CNY" in original
    assert b'fx-date: 2024-01-05' in original
    assert original.startswith(b"; preserve my comments")
    assert sync.sync(main, prices, [ASOF], fetch=fake_fetch) == []
    assert prices.read_bytes() == original


def test_dry_run_never_changes_file(ledger):
    main, prices = ledger
    original = prices.read_bytes()
    assert len(sync.sync(main, prices, [ASOF], dry_run=True, fetch=fake_fetch)) == 3
    assert prices.read_bytes() == original


def test_partial_fetch_failure_preserves_original(ledger):
    main, prices = ledger
    original = prices.read_bytes()

    def fail_fx(spec, asof, max_age):
        if "HKD-CNY" in spec:
            raise TimeoutError("offline")
        return fake_fetch(spec, asof, max_age)

    with pytest.raises(sync.SyncError, match="offline"):
        sync.sync(main, prices, [ASOF], fetch=fail_fx)
    assert prices.read_bytes() == original
    assert not prices.with_name("prices.bean.sync.lock").exists()


def test_missing_commodity_is_not_silently_ignored(ledger):
    main, prices = ledger
    main.write_text(LEDGER.replace('  price: "HKD:test/TEST"', ''), encoding="utf-8")
    with pytest.raises(sync.SyncError, match="Missing commodity"):
        sync.sync(main, prices, [ASOF], fetch=fake_fetch)


def test_conflict_rejects_whole_batch(ledger):
    main, prices = ledger
    prices.write_text("2024-01-05 price HK.TEST 8 CNY\n", encoding="utf-8")
    original = prices.read_bytes()
    with pytest.raises(sync.SyncError, match="Conflicting price"):
        sync.sync(main, prices, [ASOF], fetch=fake_fetch)
    assert prices.read_bytes() == original


def test_historical_holdings_exclude_future_purchase(ledger):
    main, prices = ledger
    assert sync.sync(main, prices, [date(2024, 1, 1)], fetch=fake_fetch) == []


def test_concurrent_ledger_edit_is_detected(ledger):
    main, prices = ledger
    original = prices.read_bytes()

    def edit_during_fetch(spec, asof, max_age):
        main.write_text(LEDGER + '\n; concurrent edit\n', encoding="utf-8")
        return fake_fetch(spec, asof, max_age)

    with pytest.raises(sync.SyncError, match="Ledger changed"):
        sync.sync(main, prices, [ASOF], fetch=edit_during_fetch)
    assert prices.read_bytes() == original
    assert not list(prices.parent.glob(".price-sync-*.tmp"))


def test_active_lock_prevents_sync(ledger):
    main, prices = ledger
    lock = prices.with_name("prices.bean.sync.lock")
    lock.touch()
    with pytest.raises(sync.SyncError, match="Another sync"):
        sync.sync(main, prices, [ASOF], fetch=fake_fetch)
    assert lock.exists()


@pytest.mark.parametrize("value,stamp,currency", [
    ("NaN", "2024-01-05T15:00:00+08:00", "CNY"),
    ("-1", "2024-01-05T15:00:00+08:00", "CNY"),
    ("1", "2024-01-06T15:00:00+08:00", "CNY"),
    ("1", "2023-12-01T15:00:00+08:00", "CNY"),
    ("1", "2024-01-05T15:00:00", "CNY"),
    ("1", "2024-01-05T15:00:00+08:00", "HKD"),
])
def test_quote_integrity(value, stamp, currency):
    quote = source.SourcePrice(Decimal(value), datetime.fromisoformat(stamp), currency)
    with pytest.raises(sync.SyncError):
        sync.check_quote(quote, "CNY", ASOF, 7)


def test_month_ends_include_leap_year():
    assert list(sync.month_ends(date(2024, 1, 15), date(2024, 3, 1))) == [
        date(2024, 1, 31), date(2024, 2, 29)]


def test_fx_cannot_postdate_native_quote(ledger):
    main, prices = ledger

    def future_fx(spec, asof, max_age):
        quote, observed, provenance = fake_fetch(spec, asof, max_age)
        if "HKD-CNY" in spec:
            quote = quote._replace(time=datetime(2024, 1, 6, tzinfo=timezone.utc))
        return quote, observed, provenance

    with pytest.raises(sync.SyncError, match="outside"):
        sync.sync(main, prices, [ASOF], fetch=future_fx)

def test_configured_fallback_after_primary_network_failure():
    from types import SimpleNamespace
    from unittest.mock import Mock, patch
    from beanprice.price import PriceSource

    primary = Mock()
    primary.get_historical_price.side_effect = TimeoutError("offline")
    secondary = Mock()
    secondary.get_historical_price.return_value = source.SourcePrice(
        Decimal("72.45"), datetime(2024, 1, 5, tzinfo=timezone.utc), "HKD")
    sources = [PriceSource(SimpleNamespace(__name__="primary", Source=lambda: primary),
                           "02020", False),
               PriceSource(SimpleNamespace(__name__="secondary", Source=lambda: secondary),
                           "02020", False)]
    with patch.object(sync, "parse_source_map", return_value={"HKD": sources}):
        quote, observed, provenance = sync.fetch_quote("ignored", ASOF, 7)
    assert quote.price == Decimal("72.45")
    assert provenance == "secondary/02020"
    assert observed == ASOF

def test_extended_age_limit_expands_series_request():
    from types import SimpleNamespace
    from unittest.mock import patch
    from beanprice.price import PriceSource

    class HolidaySource(source.Source):
        def get_prices_series(self, symbol, begin, end):
            assert (end - begin).days == 30
            return [source.SourcePrice(Decimal("10"),
                    datetime(2023, 12, 15, tzinfo=timezone.utc), "CNY")]

    module = SimpleNamespace(__name__="holiday", Source=HolidaySource)
    with patch.object(sync, "parse_source_map",
                      return_value={"CNY": [PriceSource(module, "TEST", False)]}):
        quote, observed, _ = sync.fetch_quote("ignored", ASOF, 30)
    assert observed == date(2023, 12, 15)
    assert quote.price == Decimal("10")
