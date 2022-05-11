import logging
from ruamel import yaml as yaml
from typing import Any, Dict, List, Optional, Text, Tuple, Union, Type

logger = logging.getLogger(__name__)


class DIMECache:
    def __init__(self, cache_dir: Text = None):
        self.cache_dir = cache_dir

    def get_cached_feature_importance_scores(self):
        pass
