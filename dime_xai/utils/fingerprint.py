import json
import logging
from typing import Union, Dict, OrderedDict, DefaultDict, Text, NoReturn, Optional

from rasa.shared.utils.io import deep_container_fingerprint

from dime_xai.shared.constants import (
    DEFAULT_FINGERPRINT_PERSIST_PATH,
    DEFAULT_DATA_FINGERPRINT_PERSIST_PATH,
    DEFAULT_MODEL_FINGERPRINT_PERSIST_PATH,
)
from dime_xai.shared.exceptions.dime_core_exceptions import (
    ModelFingerprintPersistException,
    DataFingerprintPersistException,
    DIMEFingerprintPersistException
)
from dime_xai.utils.io import get_timestamp_str

logger = logging.getLogger(__name__)


def generate_model_fingerprint(
        model_metadata: Union[Dict, OrderedDict, DefaultDict],
        persist: bool = False,
        persist_file_path: Text = DEFAULT_MODEL_FINGERPRINT_PERSIST_PATH
) -> Optional[Text]:
    fingerprint = deep_container_fingerprint(model_metadata)
    if persist:
        try:
            with open(persist_file_path, encoding='utf8', mode='w') as fingerprint_cache:
                json.dump({
                    "model_fingerprint": fingerprint,
                    "timestamp": get_timestamp_str(sep="-")
                }, fingerprint_cache, indent=4, ensure_ascii=False)
        except Exception as e:
            raise ModelFingerprintPersistException(f"Failed to persist the model fingerprint. {e}")

    return fingerprint


def generate_dataset_fingerprint(
        dataset_metadata: Union[Dict, OrderedDict, DefaultDict],
        persist: bool = False,
        persist_file_path: Text = DEFAULT_DATA_FINGERPRINT_PERSIST_PATH
) -> NoReturn:
    fingerprint = deep_container_fingerprint(dataset_metadata)
    if persist:
        try:
            with open(persist_file_path, encoding='utf8', mode='w') as fingerprint_cache:
                json.dump({
                    "data_fingerprint": fingerprint,
                    "timestamp": get_timestamp_str(sep="-")
                }, fingerprint_cache, indent=4, ensure_ascii=False)
        except Exception as e:
            raise DataFingerprintPersistException(f"Failed to persist the data fingerprint. {e}")


class Fingerprint:
    def __init__(
            self,
            model_fingerprint,
            data_fingerprint,
            persist_file_path: Text = DEFAULT_FINGERPRINT_PERSIST_PATH
    ) -> NoReturn:
        self.model_fingerprint = model_fingerprint
        self.data_fingerprint = data_fingerprint
        self.persist_file_path = persist_file_path

    def persist(
            self,
            persist_file_path: Text = DEFAULT_FINGERPRINT_PERSIST_PATH,
    ):
        try:
            with open(persist_file_path, encoding='utf8', mode='w') as fingerprint_cache:
                json.dump(
                    {
                        "model_fingerprint": self.model_fingerprint,
                        "data_fingerprint": self.data_fingerprint,
                        "dime_fingerprint": deep_container_fingerprint([self.model_fingerprint, self.data_fingerprint]),
                        "timestamp": get_timestamp_str(sep="-")
                    },
                    fingerprint_cache,
                    indent=4,
                    ensure_ascii=False
                )
        except Exception as e:
            raise DIMEFingerprintPersistException(f"Failed to persist the data fingerprint. {e}")
