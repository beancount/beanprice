# Safe end-of-day valuation

Install this fork into the same Python environment as Fava and Beancount:

```powershell
python -m pip install -e .
python -c "import beanprice.sync; print(beanprice.sync.__file__)"
```

Declare each security in its **native quote currency**. FX declarations give the
conversion into the reporting currency:

```beancount
2010-01-01 commodity HK.02020
  price: "HKD:eastmoneystock/02020"
2010-01-01 commodity HKD
  price: "CNY:ecbrates/HKD-CNY"
```

Use `eastmoneystock` for exchange closing prices of supported Shanghai/Shenzhen
A shares, ETFs and HKD Hong Kong counters; use `eastmoneyfund` for off-exchange
fund unit NAV. B shares and Hong Kong RMB counters are rejected rather than
being assigned the wrong currency. Do not substitute adjusted prices for raw
closing prices. These East Money APIs are undocumented and may change.

```powershell
bean-price-sync main.bean --output account/price.bean --dry-run
bean-price-sync main.bean --output account/price.bean
bean-price-sync main.bean --output account/price.bean --date 2026-08-31
bean-price-sync main.bean --output account/price.bean --month-ends 2026-01-01 2026-08-31
```

The default is yesterday in UTC+8. Only completed dates before today are
accepted. Quotes retain their actual trading/NAV date: weekends and holidays
are not relabelled as trading days. `--max-age` defaults to 7 **calendar days**
and applies independently to the security and its FX rate; extended exchange
holidays or suspensions require an explicit, reviewed larger value. This is an
age threshold, not an exchange trading-calendar implementation.

Only assets held at the end of each requested date are fetched, including
foreign cash. A missing declaration/source is an error. The legacy
`commodity_skip` allocation metadata does not suppress price coverage.
A source declaration may list comma-separated alternatives under one native
currency (standard bean-price syntax). Sources with inverted output are not
supported; configure an explicit BASE-QUOTE provider instead.

For HKD holdings the file stores the HKD close, a dated HKD/CNY rate, and the
product as a direct CNY price (rounded to 8 decimal places). The product's
metadata preserves the native value, both sources, FX date and FX rate.
ECB cross rates use same-date EUR reference observations and are valuation
rates, **not** Stock Connect execution or settlement rates. FX is selected as
of the native quote date. This is end-of-day accounting, not an intraday
backtesting feed: provider observation dates are not publication timestamps.
Existing CNY lot costs, cash settlements and realized gains are untouched.

All required fetches and ledger validation complete before any write. Identical
(date, commodity, currency, value) records are skipped, conflicting values stop
the batch for manual review. Existing output text/comments are preserved.
The output must already be included in the ledger and contain only prices.
A sibling temporary file is flushed and atomically replaces the original;
concurrent syncs are locked and changes to loaded ledger inputs abort the write.
After a process crash, inspect `.sync.lock` before removing a stale lock.
`--dry-run` checks everything and prints proposed records without changing prices.
The CLI exits nonzero on failure; do not pipe its output into the ledger.

Run the focused offline regression suite on Windows or Linux:

```powershell
python -m pytest beanprice/sync_test.py beanprice/sources/valuation_test.py beanprice/sources/eastmoneystock_test.py beanprice/sources/eastmoneyfund_test.py beanprice/sources/ecbrates_test.py beanprice/sources/tencent_test.py
```

The complete offline suite can be run with `python -m pytest beanprice`.
On Windows, the nine tests requiring POSIX process timezone switching are
explicitly skipped; provider tests that do not require switching still run.
Linux CI also exercises those POSIX tests. Live checks remain deliberate,
read-only smoke tests; unit tests do not depend on Yahoo authentication/network.

Tencent (`tencent/02020`) is an explicit alternative for native unadjusted
stock/ETF closing prices, for example `HKD:eastmoneystock/02020,tencent/02020`.
Actual successful source names are recorded on every saved quote.
