#!/usr/bin/env python3
""" Install script for beanprice. """

__copyright__ = "Copyright (C) 2008-2020  Martin Blais"
__license__ = "GNU GPLv2"

from setuptools import setup, find_packages


setup(name="beanprice",
      version='1.2.0',
      description="Price quotes fetcher for Beancount",
      long_description=
      """
      A script to fetch market data prices from various sources on the internet
      and render them for plain text accounting price syntax (and Beancount).
      """,

      license="GNU GPLv2 only",
      author="Martin Blais",
      author_email="blais@furius.ca",
      url="http://github.com/beancount/beanprice",
      download_url="https://github.com/beancount/beanprice",
      packages=find_packages(),

      install_requires=[
          # Beancount library itself.
          'beancount>=2.3.4',

          # Testing support now uses the pytest module.
          'pytest',

          # This is required to parse dates from command-line options in a
          # loose, accepting format. Note that we use dateutil for timezone
          # database definitions as well, although it is inferior to pytz, but
          # because it can use the OS timezone database in the Windows
          # registry. See this article for context:
          # https://www.assert.cc/2014/05/25/which-python-time-zone-library.html
          # However, for creating offset timezones, we use the datetime.timezone
          # helper class because it is built-in.
          # Where this matters is for price source fetchers.
          # (Note: If pytz supported the Windows registry timezone information,
          # I would switch to that.)
          'python-dateutil',

          # This library is needed to make requests for price sources.
          'requests',
      ],

      entry_points={
          'console_scripts': [
              'bean-price = beanprice.price:main',
          ]
      },

      python_requires='>=3.5')
