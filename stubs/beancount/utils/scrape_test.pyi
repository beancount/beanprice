from beancount.utils import scrape as scrape, test_utils as test_utils
from collections import namedtuple
from typing import Any

class TestScrapeFunctions(test_utils.TestCase):
    test_html: Any = ...
    def test_iterlinks(self) -> None: ...

Redirect = namedtuple('Redirect', 'target_url')

class TestScrapeURLs(test_utils.TestCase):
    web_contents: Any = ...
    def fetch_url(url: Any): ...
    def callback(self, url: Any, response: Any, unused_contents: Any, html_root: Any, unused_skipped_urls: Any) -> None: ...
    results: Any = ...
    def test_scrape_urls(self) -> None: ...

class TestScrapeVerification(test_utils.TestCase):
    def test_validate_local_links(self) -> None: ...
    def test_validate_local_links__empty(self) -> None: ...
