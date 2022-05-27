import logging
from typing import Text, NoReturn

from dime_xai.shared.constants import DEFAULT_CACHE_PATH
from dime_xai.utils.io import _create_cache_dir

logger = logging.getLogger(__name__)


def initialize_cache_dir(
        cache_dir: Text = DEFAULT_CACHE_PATH
) -> NoReturn:
    """
    Creates the cache directory if
    it does not exist

    Args:
        cache_dir: a custom path to create the
            DIME cache directory

    Returns:
        no return
    """
    _create_cache_dir(cache_data_dir=cache_dir)


class DIMECache:
    """
    DIME cache container
    """

    def __init__(self, cache_dir: Text = DEFAULT_CACHE_PATH):
        self.cache_dir = cache_dir
        initialize_cache_dir(cache_dir)
