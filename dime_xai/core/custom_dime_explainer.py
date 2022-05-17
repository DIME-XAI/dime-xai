import logging
from typing import Text, Optional, List

from dime_xai.core.dime_explainer import DIMEExplainer
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
    MODEL_TYPE_OTHER,
    MODEL_MODE_LOCAL,
    MODEL_MODE_REST,
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
from dime_xai.shared.explanation import DIMEExplanation
from dime_xai.shared.testing_data.custom_testing_data import CustomTestingData

logger = logging.getLogger(__name__)


class CustomDIMEExplainer(DIMEExplainer):
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
            output_mode: Text = DEFAULT_OUTPUT_MODE,
    ) -> None:
        super().__init__(
            models_path=models_path,
            model_name=model_name,
            testing_data_path=testing_data_path,
            model_mode=model_mode,
            url=url,
            data_instances=data_instances,
            ranking_length=ranking_length,
            ngrams=ngrams,
            max_ngrams=max_ngrams,
            min_ngrams=min_ngrams,
            case_sensitive=case_sensitive,
            metric=metric,
            testing_data_encoding=testing_data_encoding,
            testing_data_read_mode=testing_data_read_mode,
            file_extensions=file_extensions,
            nlu_tag=nlu_tag,
            testing_data_tag=testing_data_tag,
            version_tag=version_tag,
            testing_data_version=testing_data_version,
            model_type=MODEL_TYPE_OTHER,
            output_mode=output_mode,
        )
        self.testing_data = CustomTestingData(testing_data_path)

    def explain(
            self
    ) -> Optional[DIMEExplanation]:
        # TODO :implement
        print(self.url)

        if self.model_mode == MODEL_MODE_LOCAL:
            print("You're executing a local model")
        elif self.model_mode == MODEL_MODE_REST:
            print("You're executing a rest model")

        print(
            self.models_path,
            self.testing_data_path,
            self.model_mode,
            self.url,
            self.data_instances,
            self.ranking_length,
            self.testing_data_encoding,
            self.testing_data_read_mode,
            self.file_extensions,
            self.nlu_tag,
            self.testing_data_tag,
            self.version_tag,
            self.testing_data_version,
            self.testing_data,
            sep="\n"
        )
        return None
