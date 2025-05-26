# beanprice: Price quotes fetcher for Beancount

## Description

A script to fetch market data prices from various sources on the internet
and render them for plain text accounting price syntax (and Beancount).

This used to be located within Beancount itself (at v2) under beancount.prices.
This repo will contain all future updates to that script and to those price
sources.

## Documentation

Some documentation is still part of Beancount. More about how to use this can be
found on that [mailing-list](https://groups.google.com/forum/#!forum/beancount).
Otherwise read the source.

## Quick start

To install beanprice, run:

```shell
pip install git+https://github.com/beancount/beanprice.git
```

You can fetch the latest price of a stock by running:

```shell
bean-price -e 'USD:yahoo/AAPL'
```

To fetch the latest prices from your beancount file, first ensure that commodities have price metadata, e.g.

```
2000-01-01 commodity AAPL
  price: "USD:yahoo/AAPL"
```

Then run:

```shell
bean-price ledger.beancount
```

To update prices up to the present day, run:

```shell
bean-price --update ledger.beancount
```

For more detailed guide for price fetching, read <https://beancount.github.io/docs/fetching_prices_in_beancount.html>.


## Price source info
The following price sources are available:

| Name                    | Module                    | Provides prices for                                                               | Base currency                                                                    | Latest price? | Historical price? |
|-------------------------|---------------------------|-----------------------------------------------------------------------------------|----------------------------------------------------------------------------------|---------------|-------------------|
| Alphavantage            | `beanprice.alphavantage`  | [Stocks, FX, Crypto](http://alphavantage.co)                                      | Many currencies                                                                  | ✓             | ✕                 |
| Coinbase                | `beanprice.coinbase`      | [Most common (crypto)currencies](https://api.coinbase.com/v2/exchange-rates)      | [Many currencies](https://api.coinbase.com/v2/currencies)                        | ✓             | ✓                 |
| Coincap                 | `beanprice.coincap`       | [Most common (crypto)currencies](https://docs.coincap.io)                         | USD                                                                              | ✓             | ✓                 |
| Coinmarketcap           | `beanprice.coinmarketcap` | [Most common (crypto)currencies](https://coinmarketcap.com/api/documentation/v1/) | Many Currencies                                                                  | ✓             | ✕                 |
| Euronext                | `beanprice.euronext`      | [Trading symbols](https://www.euronext.com/en/list-products)                      | EUR                                                                              | ✓             | ✓                 |
| European Central Bank API| `beanprice.ecbrates`      | [Many currencies](https://data.ecb.europa.eu/search-results?searchTerm=exchange%20rates)                     | [Many currencies](https://data.ecb.europa.eu/search-results?searchTerm=exchange%20rates) (Derived from EUR rates)| ✓             | ✓                |
| IEX                     | `beanprice.iex`           | [Trading symbols](https://iextrading.com/trading/eligible-symbols/)               | USD                                                                              | ✓             | 🚧 (Not yet!)     |
| OANDA                   | `beanprice.oanda`         | [Many currencies](https://developer.oanda.com/exchange-rates-api/v1/currencies/)  | [Many currencies](https://developer.oanda.com/exchange-rates-api/v1/currencies/) | ✓             | ✓                 |
| Quandl                  | `beanprice.quandl`        | [Various datasets](https://www.quandl.com/search)                                 | [Various datasets](https://www.quandl.com/search)                                | ✓             | ✓                 |
| Rates API               | `beanprice.ratesapi`      | [Many currencies](https://api.exchangerate.host/symbols)                          | [Many currencies](https://api.exchangerate.host/symbols)                         | ✓             | ✓                 |
| Thrift Savings Plan     | `beanprice.tsp`           | TSP Funds                                                                         | USD                                                                              | ✓             | ✓                 |
| Yahoo                   | `beanprice.yahoo`         | Many currencies                                                                   | Many currencies                                                                  | ✓             | ✓                 |
| EastMoneyFund(天天基金) | `beanprice.eastmoneyfund` | [Chinese Funds](http://fund.eastmoney.com/js/fundcode_search.js)                  | CNY                                                                              | ✓             | ✓                 |


More price sources can be found at [awesome-beancount.com](https://awesome-beancount.com/#price-sources) website.

## Creating a custom price source

To create a price source, create a package (i.e. `my_package`) with a module (i.e. `my_module`) that contains the Source class which inherits from the `beanprice.Source` class:

```python
from beanprice import source

class Source(source.Source):
  def get_latest_price(self, ticker) -> source.SourcePrice | None:
    pass
  
  def get_historical_price(self, ticker, time):
    pass
```
Implement the logic for fetching the prices. At a minimum, the `get_latest_price()` is required.

Then use your price source in the commodities

```beancount
1900-01-01 commodity XYZ
  price: "AUD:my_package.my_module/XYZ"
```
`AUD` just being an example of a currency specification.

## Testing

Run tests:

```
pytest beanprice
```

Lint:

```
pylint beanprice
```

Type checker:

```
mypy beanprice
```

## Copyright and License

Copyright (C) 2007-2020  Martin Blais.  All Rights Reserved.

This code is distributed under the terms of the "GNU GPLv2 only".
See COPYING file for details.
