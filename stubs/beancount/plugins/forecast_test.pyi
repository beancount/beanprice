from beancount import loader as loader
from beancount.parser import cmptest as cmptest

class TestExampleForecast(cmptest.TestCase):
    def test_forecast(self) -> None: ...
