import unittest
from beancount.ingest import cache as cache, importer as importer

class TestImporterProtocol(unittest.TestCase):
    def test_importer_methods(self) -> None: ...
