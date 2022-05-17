import logging
from typing import Text

from dime_xai.shared.constants import DEFAULT_CACHE_PATH
from dime_xai.utils.io import _create_cache_dir

logger = logging.getLogger(__name__)


def initialize_cache_dir(cache_dir: Text = DEFAULT_CACHE_PATH):
    _create_cache_dir(cache_data_dir=cache_dir)


class DIMECache:
    def __init__(self, cache_dir: Text = DEFAULT_CACHE_PATH):
        self.cache_dir = cache_dir
        initialize_cache_dir(cache_dir)
