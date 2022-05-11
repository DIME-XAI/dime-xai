from typing import Union, Dict, OrderedDict, DefaultDict, List, Tuple, Text

from dime_xai.shared.constants import (
    DEFAULT_FINGERPRINT_PERSIST_PATH,
)


def _fingerprint(
        non_fingerprinted_object: Union[Dict, OrderedDict, DefaultDict, List, Tuple]
):
    return None


def generate_model_fingerprint(
        model_metadata: Union[Dict, OrderedDict, DefaultDict],
        persist: bool = False,
        persist_file_path: Text = DEFAULT_FINGERPRINT_PERSIST_PATH
):
    pass


def generate_dataset_fingerprint(
        dataset_metadata: Union[Dict, OrderedDict, DefaultDict],
        persist: bool = False,
        persist_file_path: Text = DEFAULT_FINGERPRINT_PERSIST_PATH
):
    pass


class Fingerprint:
    def __init__(self, model_fingerprint, data_fingerprint):
        self.model_fingerprint = model_fingerprint
        self.data_fingerprint = data_fingerprint

    def persist_fingerprint(
            self,
            persist_file_path: Text = DEFAULT_FINGERPRINT_PERSIST_PATH,
    ):
        pass
