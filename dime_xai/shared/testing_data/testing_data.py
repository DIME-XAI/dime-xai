import logging
from typing import List, Optional, Text, NoReturn

from dime_xai.shared.constants import (
    DEFAULT_DATA_PATH,
    DEFAULT_CASE_SENSITIVE_MODE,
)

logger = logging.getLogger(__name__)


class TestingData:
    def __init__(
            self,
            testing_data_dir: Text = DEFAULT_DATA_PATH,
            case_sensitive: bool = DEFAULT_CASE_SENSITIVE_MODE
    ):
        self._testing_data_dir = testing_data_dir
        self._testing_data = None
        self._tagged_testing_data = None
        self._tokens = list()
        self._vocabulary = list()
        self._fingerprint = None
        self.case_sensitive = case_sensitive

    @staticmethod
    def _tag_examples(testing_data: List) -> List:
        pass

    def _initialize_testing_data(self) -> NoReturn:
        pass

    def get_instances(self, intent: Text = None) -> Optional[List]:
        pass

    def get_instance_size(self, intent: Text = None) -> Optional[int]:
        pass

    def get_intents(self) -> Optional[List]:
        pass

    def get_intent_size(self, ) -> Optional[int]:
        pass
