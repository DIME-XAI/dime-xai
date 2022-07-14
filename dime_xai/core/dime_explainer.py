import logging
from typing import Text, List

from dime_xai.shared.constants import (
    DEFAULT_DATA_PATH,
    DEFAULT_MODELS_PATH,
    YAML_EXTENSIONS,
    DEFAULT_NLU_YAML_TAG,
    DEFAULT_VERSION_YAML_TAG,
    DEFAULT_NLU_YAML_VERSION,
    FILE_ENCODING_UTF8,
    FILE_READ_PERMISSION,
    DEFAULT_NLU_EXAMPLES_TAG,
    DEFAULT_MODEL_TYPE,
    DEFAULT_MODEL_MODE,
    MODEL_REST_WEBHOOK_URL,
    DEFAULT_RANKING_LENGTH,
    DEFAULT_OUTPUT_MODE,
    DEFAULT_LATEST_TAG,
    DEFAULT_NGRAMS_MODE,
    DEFAULT_MAX_NGRAMS,
    DEFAULT_MIN_NGRAMS,
    DEFAULT_CASE_SENSITIVE_MODE, Metrics,
)

logger = logging.getLogger(__name__)


class DIMEExplainer:
    def __init__(
            self,
            models_path: Text = DEFAULT_MODELS_PATH,
            model_name: Text = DEFAULT_LATEST_TAG,
            testing_data_path: Text = DEFAULT_DATA_PATH,
            model_mode: Text = DEFAULT_MODEL_MODE,
            url: Text = MODEL_REST_WEBHOOK_URL,
            data_instances: List = None,
            ranking_length: int = DEFAULT_RANKING_LENGTH,
            ngrams: bool = DEFAULT_NGRAMS_MODE,
            max_ngrams: int = DEFAULT_MAX_NGRAMS,
            min_ngrams: int = DEFAULT_MIN_NGRAMS,
            case_sensitive: bool = DEFAULT_CASE_SENSITIVE_MODE,
            metric: Text = Metrics.F1_SCORE,
            testing_data_encoding: Text = FILE_ENCODING_UTF8,
            testing_data_read_mode: Text = FILE_READ_PERMISSION,
            file_extensions: Text = YAML_EXTENSIONS,
            nlu_tag: Text = DEFAULT_NLU_YAML_TAG,
            testing_data_tag: Text = DEFAULT_NLU_EXAMPLES_TAG,
            version_tag: Text = DEFAULT_VERSION_YAML_TAG,
            testing_data_version: Text = DEFAULT_NLU_YAML_VERSION,
            model_type: Text = DEFAULT_MODEL_TYPE,
            output_mode: Text = DEFAULT_OUTPUT_MODE,
            quiet_mode: bool = False,
    ):
        self.models_path = models_path
        self.model_name = model_name
        self.testing_data_path = testing_data_path
        self.file_extensions = file_extensions
        self.model_mode = model_mode
        self.url = url
        self.data_instances = data_instances
        self.ranking_length = ranking_length
        self.ngrams = ngrams
        self.max_ngrams = max_ngrams
        self.min_ngrams = min_ngrams
        self.case_sensitive = case_sensitive
        self.metric = metric
        self.testing_data_encoding = testing_data_encoding
        self.testing_data_read_mode = testing_data_read_mode
        self.nlu_tag = nlu_tag
        self.version_tag = version_tag
        self.testing_data_tag = testing_data_tag
        self.testing_data_version = testing_data_version
        self.model_type = model_type
        self.output_mode = output_mode
        self.quiet_mode = quiet_mode
