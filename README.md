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
mypy beanprice --ignore-missing-imports
```

## Copyright and License

Copyright (C) 2007-2020  Martin Blais.  All Rights Reserved.

This code is distributed under the terms of the "GNU GPLv2 only".
See COPYING file for details.
