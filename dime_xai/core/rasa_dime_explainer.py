import logging
import time
from time import process_time
from typing import Text, Dict, Optional, List, Sequence

from dime_xai.core.dime_core import (
    global_feature_importance,
    exp_norm_softmax,
    local_feature_importance,
    feature_selection,
    dual_feature_importance,
)
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
    MODEL_TYPE_DIET,
    DEFAULT_MODEL_MODE,
    MODEL_REST_WEBHOOK_URL,
    DEFAULT_RANKING_LENGTH,
    DEFAULT_OUTPUT_MODE,
    DEFAULT_LATEST_TAG,
    DEFAULT_MAX_NGRAMS,
    DEFAULT_MIN_NGRAMS,
    DEFAULT_NGRAMS_MODE,
    DEFAULT_CASE_SENSITIVE_MODE,
    Metrics,
    OUTPUT_MODE_GLOBAL,
    OUTPUT_MODE_LOCAL,
    OUTPUT_MODE_DUAL,
    MODEL_MODE_REST,
    MODEL_MODE_LOCAL,
    RASA_CORE_VERSION,
)
from dime_xai.shared.explanation import DIMEExplanation
from dime_xai.shared.model.rasa_model import RASAModel
from dime_xai.shared.testing_data.rasa_testing_data import RASATestingData
from dime_xai.utils.fingerprint import Fingerprint
from dime_xai.utils.io import get_timestamp_str, exit_dime
from dime_xai.utils.text_preprocessing import (
    bag_of_words,
    remove_token_from_dataset,
    lowercase_list,
    get_token_count,
)

logger = logging.getLogger(__name__)


class RasaDIMEExplainer(DIMEExplainer):
    def __init__(
            self,
            models_path: Text = DEFAULT_MODELS_PATH,
            model_name: Text = DEFAULT_LATEST_TAG,
            testing_data_path: Text = DEFAULT_DATA_PATH,
            model_mode: Text = DEFAULT_MODEL_MODE,
            rasa_version: Text = RASA_CORE_VERSION,
            url: Text = MODEL_REST_WEBHOOK_URL,
            data_instances: List = None,
            ranking_length: int = DEFAULT_RANKING_LENGTH,
            ngrams: bool = DEFAULT_NGRAMS_MODE,
            max_ngrams: int = DEFAULT_MAX_NGRAMS,
            min_ngrams: int = DEFAULT_MIN_NGRAMS,
            case_sensitive: bool = DEFAULT_CASE_SENSITIVE_MODE,
            global_metric: Text = Metrics.F1_SCORE,
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
            global_metric=global_metric,
            testing_data_encoding=testing_data_encoding,
            testing_data_read_mode=testing_data_read_mode,
            file_extensions=file_extensions,
            nlu_tag=nlu_tag,
            testing_data_tag=testing_data_tag,
            version_tag=version_tag,
            testing_data_version=testing_data_version,
            model_type=MODEL_TYPE_DIET,
            output_mode=output_mode,
        )
        self.rasa_version = rasa_version
        self.testing_data = RASATestingData(
            testing_data_dir=self.testing_data_path,
            case_sensitive=self.case_sensitive,
            from_rasa=True,
        )
        self.model = RASAModel(
            model_mode=self.model_mode,
            models_path=self.models_path,
            model_name=self.model_name,
            url=self.url,
        )
        self.fingerprint = Fingerprint(
            model_fingerprint=self.model.get_fingerprint(),
            data_fingerprint=self.testing_data.get_fingerprint(),
        )
        if not self.case_sensitive:
            self.data_instances = lowercase_list(self.data_instances)

        # check if custom DIET was used when the
        # metric has been specified as 'confidence'
        if self.model and self.global_metric == Metrics.CONFIDENCE:
            if not self.model.test_diet_compatibility(intents=self.testing_data.get_intents()):
                logger.error(f"Incompatible DIET classifier. Either use 'accuracy' "
                             f"or 'f1-score' as the metric or attach a custom DIET "
                             f"classifier that can output all confidence scores to use "
                             f"confidence as the global metric. "
                             f"http://dimedocs/custom-diet")
                exit_dime(1)

        init_model_parse_start_time = process_time()
        self.init_model_output = self.model.parse_supervised_batch(
            data_instances=self.testing_data.get_testing_data(),
            description="Parsing all tokens"
        )
        init_model_parse_end_time = process_time()
        init_model_parse_duration = init_model_parse_end_time - init_model_parse_start_time
        logger.info(f"Initial dataset was parsed within {init_model_parse_duration} seconds.")
        logger.debug('Initialized the DIME explainer')
        self._init_cache()

    def _init_cache(self):
        # model_fingerprint = self.model.get_fingerprint()
        # data_fingerprint = self.testing_data.get_fingerprint()
        # # handle caches
        # # TODO :check fingerprints
        # # TODO :check cache if same prints
        # # TODO :load cache files if available
        pass

    def _global(self, vocabulary: List) -> Optional[Dict]:
        gfi_start_time = time.time()
        instance_global_feature_importance = dict()

        testing_data = self.testing_data.get_testing_data()
        testing_tokens = self.testing_data.get_tokens()
        init_model_output = self.init_model_output

        for token in vocabulary:
            token_count = get_token_count(testing_tokens, token)

            if token_count > 0:
                modified_testing_data = remove_token_from_dataset(
                    testing_data=testing_data,
                    token=token
                )

                token_model_output = self.model.parse_supervised_batch(
                    data_instances=modified_testing_data,
                    description=f"Parsing token [{vocabulary.index(token) + 1}/{len(vocabulary)}]"
                )
                logger.info(f"Found {token_count} instances of the token '{token}'")

                global_feature_importance_score = global_feature_importance(
                    init_model_output=init_model_output,
                    token_model_output=token_model_output,
                    token=token,
                    scorer=self.global_metric
                )
                logger.info(f'{str.capitalize(self.global_metric)} difference for the token '
                            f'`{token}`: {global_feature_importance_score}')
            else:
                global_feature_importance_score = 0
                if self.case_sensitive:
                    logger.warning(f"Token `{token}` was not found in the vocabulary. Global feature importance "
                                   f"score was set to 0 by default. Note that `case_sensitive` can be set to "
                                   f"`False` in the dime config file to discard the case if required.")
                else:
                    logger.warning(f"Token `{token}` was not found in the vocabulary. Global feature importance "
                                   f"score was set to 0 by default.")

            instance_global_feature_importance[token] = global_feature_importance_score

        # Ordering the dict by gfi value
        ordered_gfi = {
            k: v for k, v in sorted(
                instance_global_feature_importance.items(),
                key=lambda x: x[1],
                reverse=True)
        }
        gfi_end_time = time.time()
        gfi_duration = gfi_end_time - gfi_start_time
        if gfi_duration < 60:
            logger.info(f"Global feature importance was calculated within {gfi_duration} seconds.")
        elif 60 <= gfi_duration < 3600:
            logger.info(f"Global feature importance was calculated within {gfi_duration / 60} minutes.")
        elif 3600 <= gfi_duration < 86400:
            logger.info(f"Global feature importance was calculated within {gfi_duration / 3600} hours.")
        return ordered_gfi

    def _instance_global_local(self, instance: Text) -> Sequence[Dict]:
        # Getting global feature importance for tokens
        # present in the instance
        instance_vocab = bag_of_words(instances=instance)
        global_scores = self._global(vocabulary=instance_vocab)
        global_selection = feature_selection(
            global_scores=global_scores,
            ranking_length=self.ranking_length
        )
        global_weights = exp_norm_softmax(vector=global_selection)

        # Getting local feature importance for tokens
        # present in the instance
        local_scores = local_feature_importance(selected_tokens=list(global_selection.keys()))
        local_weights = exp_norm_softmax(vector=local_scores)

        return global_scores, global_selection, global_weights, local_scores, local_weights

    def explain(self, persist: bool = True) -> Optional[DIMEExplanation]:
        explanation = dict()
        explanation['timestamp'] = {'start': get_timestamp_str(sep="-"), 'end': 'unknown'}

        if self.output_mode == OUTPUT_MODE_GLOBAL:
            logger.info(f"Calculating global feature importance "
                        f"for all tokens in the dataset")

            testing_vocab = self.testing_data.get_vocabulary()
            global_scores = self._global(vocabulary=testing_vocab)
            global_weights = exp_norm_softmax(vector=global_scores)
            explanation['global'] = {
                'feature_importance': global_scores,
                'softmax_score': global_weights
            }

        elif self.output_mode == OUTPUT_MODE_LOCAL:
            all_local_scores = []
            for instance in self.data_instances:
                logger.info(f"Calculating local feature "
                            f"importance for the instance: `{instance}`")
                instance_scores = {
                    'instance': instance,
                    'global': {
                        'feature_importance': {},
                        'feature_selection': {},
                        'softmax_score': {},
                    },
                    'local': {
                        'feature_importance': {},
                        'softmax_score': {},
                    },
                }

                # Getting global and local feature importance for tokens
                # present in the instance
                global_scores, global_selection, global_weights, local_scores, local_weights = \
                    self._instance_global_local(instance=instance)

                instance_scores['global']['feature_importance'] = global_scores
                instance_scores['global']['feature_selection'] = global_selection
                instance_scores['global']['softmax_score'] = global_weights
                instance_scores['local']['feature_importance'] = local_scores
                instance_scores['local']['softmax_score'] = local_weights

                all_local_scores.append(instance_scores)
            explanation['local'] = all_local_scores

        elif self.output_mode == OUTPUT_MODE_DUAL:
            all_dime_scores = []
            for instance in self.data_instances:
                logger.info(f"Calculating dual feature "
                            f"importance for the instance: `{instance}`")
                instance_scores = {
                    'instance': instance,
                    'global': {
                        'feature_importance': {},
                        'feature_selection': {},
                        'softmax_score': {},
                    },
                    'local': {
                        'feature_importance': {},
                        'softmax_score': {},
                    },
                    'dual': {
                        'feature_importance': {},
                        'softmax_score': {},
                    }
                }

                # Getting global and local feature importance for tokens
                # present in the instance
                global_scores, global_selection, global_weights, local_scores, local_weights = \
                    self._instance_global_local(instance=instance)

                # Spacing out local scores based on the
                # global feature importance scores
                dual_scores = dual_feature_importance(
                    global_selection=global_selection,
                    local_scores=local_scores,
                )
                dual_weights = exp_norm_softmax(vector=dual_scores)

                instance_scores['global']['feature_importance'] = global_scores
                instance_scores['global']['feature_selection'] = global_selection
                instance_scores['global']['softmax_score'] = global_weights
                instance_scores['local']['feature_importance'] = local_scores
                instance_scores['local']['softmax_score'] = local_weights
                instance_scores['dual']['feature_importance'] = dual_scores
                instance_scores['dual']['softmax_score'] = dual_weights

                all_dime_scores.append(instance_scores)
            explanation['dual'] = all_dime_scores

        explanation['timestamp']['end'] = get_timestamp_str(sep="-")

        explanation['config'] = {
            'case_sensitive': self.case_sensitive,
            'output_mode': self.output_mode,
            'ranking_length': self.ranking_length if self.output_mode in [OUTPUT_MODE_LOCAL, OUTPUT_MODE_DUAL] else "-",
            'global_metric': self.global_metric if self.output_mode in [OUTPUT_MODE_GLOBAL, OUTPUT_MODE_DUAL] else "-",
            'ngrams': {'min_ngrams': self.min_ngrams, 'max_ngrams': self.max_ngrams} if self.ngrams else "-"
        }
        explanation['model'] = {
            'name': self.model_name if self.model_mode == OUTPUT_MODE_LOCAL else "-",
            'type': self.model_type,
            'version': self.rasa_version if self.model_mode == MODEL_MODE_LOCAL else "-",
            'path': self.models_path if self.model_mode == MODEL_MODE_LOCAL else "-",
            'mode': self.model_mode,
            'url': self.url if self.model_mode == MODEL_MODE_REST else "-",
            'fingerprint': (self.model.get_fingerprint() if self.model_mode == MODEL_MODE_LOCAL else "-") or "-",
        }
        explanation['data'] = {
            'intents': self.testing_data.get_intent_size(),
            'instances': self.testing_data.get_instance_size(),
            'tokens': self.testing_data.get_token_size(),
            'vocabulary': self.testing_data.get_vocabulary_size(),
            'path': self.testing_data_path,
            'fingerprint': self.testing_data.get_fingerprint() or "-",
        }

        dime_explanation = DIMEExplanation(explanation=explanation)

        # # Uncomment if required to see the raw output in the terminal
        # dime_explanation.inspect()

        if persist:
            dime_explanation.persist()

        return dime_explanation
