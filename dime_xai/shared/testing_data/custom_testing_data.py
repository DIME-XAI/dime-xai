from typing import Text, NoReturn

from dime_xai.shared.testing_data.testing_data import TestingData
from dime_xai.utils import io


class CustomTestingData(TestingData):
    def __init__(self, testing_data_dir: Text = None):
        super().__init__(testing_data_dir)

    def _initialize_testing_data(self) -> NoReturn:
        self._testing_data = io.get_rasa_testing_data(self._testing_data_dir)
