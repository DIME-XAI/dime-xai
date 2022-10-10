import logging
import time
from copy import deepcopy
from time import process_time
from typing import Text, Dict, Optional, List

from tqdm import tqdm

from dime_xai.core.dime_core import (
    global_feature_importance,
    feature_selection,
    dual_feature_importance,
    min_max_normalize,
    to_probability_series,
    clip_negative_values,
)
from dime_xai.core.dime_explainer import DIMEExplainer
from dime_xai.shared.constants import (
    DEFAULT_DATA_PATH,
    DEFAULT_MODELS_PATH,
    YAML_EXTENSIONS,
    DEFAULT_NLU_YAML_TAG,
    DEFAULT_VERSION_YAML_TAG,
    DEFAULT_NLU_YAML_VERSION,
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
    OUTPUT_MODE_DUAL,
    MODEL_MODE_REST,
    MODEL_MODE_LOCAL,
    RASA_CORE_VERSION,
    FilePermission,
    Encoding,
)
from dime_xai.shared.exceptions.dime_core_exceptions import (
    InvalidMetricSpecifiedException,
    RasaExplainerException
)
from dime_xai.shared.explanation import DIMEExplanation
from dime_xai.shared.model.rasa_model import RASAModel
from dime_xai.shared.testing_data.rasa_testing_data import RASATestingData
from dime_xai.utils.cache import DIMECache
from dime_xai.utils.fingerprint import Fingerprint
from dime_xai.utils.io import get_timestamp_str
from dime_xai.utils.text_preprocessing import (
    bag_of_words,
    remove_token_from_dataset,
    lowercase_list,
    get_token_count,
    remove_token,
    order_dict,
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
            metric: Text = Metrics.F1_SCORE,
            testing_data_encoding: Text = Encoding.UTF8,
            testing_data_read_mode: Text = FilePermission.READ,
            file_extensions: Text = YAML_EXTENSIONS,
            nlu_tag: Text = DEFAULT_NLU_YAML_TAG,
            testing_data_tag: Text = DEFAULT_NLU_EXAMPLES_TAG,
            version_tag: Text = DEFAULT_VERSION_YAML_TAG,
            testing_data_version: Text = DEFAULT_NLU_YAML_VERSION,
            output_mode: Text = DEFAULT_OUTPUT_MODE,
            quiet_mode: bool = False,
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
            model_type=MODEL_TYPE_DIET,
            output_mode=output_mode,
            quiet_mode=quiet_mode,
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
            quiet_mode=quiet_mode,
        )
        self.fingerprint = Fingerprint(
            model_fingerprint=self.model.get_fingerprint(),
            data_fingerprint=self.testing_data.get_fingerprint(),
        )

        # check if custom DIET was used when the
        # metric has been specified as 'confidence'
        if self.model and self.metric == Metrics.CONFIDENCE:
            if not self.model.test_diet_compatibility(intents=self.testing_data.get_intents()):
                logger.error(f"Incompatible DIET classifier or incomplete training data intents. "
                             f"Either use 'accuracy' or 'f1-score' as the metric or attach a "
                             f"custom DIET classifier that can output all confidence scores to use "
                             f"confidence as the global metric. https://dime-xai.github.io/custom-diet")
                raise InvalidMetricSpecifiedException()

        self._cache = self._init_cache()

        if self._cache:
            logger.info(f"Successfully loaded the DIME caches\n")
            pass  # TODO :init cache checks

        if not self.case_sensitive:
            self.data_instances = lowercase_list(self.data_instances)

        init_model_parse_start_time = process_time()
        self.init_model_output = self.model.parse_supervised_batch(
            data_instances=self.testing_data.get_tagged_data(),
            description="Parsing all instances"
        )

        init_model_parse_end_time = process_time()
        init_model_parse_duration = init_model_parse_end_time - init_model_parse_start_time
        logger.info(f"Initial dataset was parsed within {init_model_parse_duration} seconds.")
        logger.debug('Initialized the DIME explainer')

    def _init_cache(self) -> Optional[DIMECache]:
        logger.debug(f"Initializing DIME caches...")

        model_fingerprint = self.model.get_fingerprint()
        data_fingerprint = self.testing_data.get_fingerprint()
        if not model_fingerprint or not data_fingerprint:
            logger.warning(f"Failed to retrieve DIME cache due to invalid "
                           f"fingerprints. DIME will run without initializing "
                           f"cache files and existing files will be overwritten")
            return None

        logger.debug(f"Received model fingerprint: {model_fingerprint}")
        logger.debug(f"Received data fingerprint: {data_fingerprint}")

        # # handle caches
        # # TODO :check fingerprints
        # # TODO :check cache if same prints
        # # TODO :load cache files if available
        return DIMECache()

    @staticmethod
    def _log_duration(duration: float, title: Text):
        if duration < 60:
            logger.info(f"{title} feature importance was calculated within {duration} seconds\n")
        elif 60 <= duration < 3600:
            logger.info(f"{title} feature importance was calculated within {duration / 60} minutes\n")
        elif 3600 <= duration < 86400:
            logger.info(f"{title} feature importance was calculated within {duration / 3600} hours.\n")

    def _global(self, vocabulary: List) -> Optional[Dict]:
        gfi_start_time = time.time()
        instance_global_feature_importance = dict()

        testing_tokens = self.testing_data.get_tokens()
        init_model_output = self.init_model_output

        for token in vocabulary:
            token_count = get_token_count(testing_tokens, token)
            testing_data = self.testing_data.get_tagged_data()

            if token_count > 0:
                modified_testing_data = remove_token_from_dataset(
                    testing_data=testing_data,
                    token=token
                )

                token_model_output = self.model.parse_supervised_batch(
                    data_instances=modified_testing_data,
                    description=f"Global feature importance [{vocabulary.index(token) + 1}/{len(vocabulary)}]"
                )

                logger.info(f"Found {token_count} instances of the token '{token}'")
                global_feature_importance_score = global_feature_importance(
                    init_model_output=init_model_output,
                    token_model_output=token_model_output,
                    token=token,
                    scorer=self.metric
                )
                logger.info(f'{str.capitalize(self.metric)} difference for the token '
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
        gfi_end_time = time.time()
        gfi_duration = gfi_end_time - gfi_start_time
        self._log_duration(duration=gfi_duration, title="Global")
        global_scores = order_dict(
            dict_to_order=instance_global_feature_importance,
            order_by_key=False,
            reverse=True
        )
        global_scores_clipped = clip_negative_values(vector=global_scores)
        global_normalized_scores = min_max_normalize(vector=global_scores_clipped)
        global_probabilities = to_probability_series(series=global_scores_clipped)
        return {
            "global_raw_scores": global_scores,
            "global_scores_clipped": global_scores_clipped,
            "global_normalized_scores": global_normalized_scores,
            "global_probabilities": global_probabilities,
        }

    def _dual(self, data_instance: Text, feature_set: Dict, filter_zeros: bool) -> Optional[Dict]:
        dfi_start_time = time.time()
        if filter_zeros:
            feature_set = {t: s for t, s in feature_set.items() if s > 0}
        if not feature_set:
            return {}

        init_instance_output = self.model.parse_unsupervised(data_instance=data_instance)
        instance_dual_feature_importance = dict()

        selected_features = list(feature_set.keys())

        if not self.quiet_mode:
            selected_features_clone = deepcopy(selected_features)
            selected_features = tqdm(selected_features)
        else:
            selected_features_clone = None

        for token in selected_features:
            modified_instance = remove_token(instance=deepcopy(data_instance), token=token)
            token_instance_output = self.model.parse_unsupervised(data_instance=modified_instance)

            dual_feature_importance_score = dual_feature_importance(
                init_instance_output=init_instance_output,
                token_instance_output=token_instance_output,
                scorer=Metrics.CONFIDENCE,
            )
            if not self.quiet_mode:
                selected_features.set_description(
                    f"Dual feature importance "
                    f"[{selected_features_clone.index(token) + 1}/{len(selected_features_clone)}]"
                )
            instance_dual_feature_importance[token] = dual_feature_importance_score
        dfi_end_time = time.time()
        dfi_duration = dfi_end_time - dfi_start_time
        self._log_duration(duration=dfi_duration, title="Dual")
        dual_result = dict()
        dual_result['predicted_intent'] = init_instance_output['predicted_intent']
        dual_result['predicted_confidence'] = init_instance_output['predicted_confidence']
        dual_result['dual_importance_scores'] = order_dict(
            dict_to_order=instance_dual_feature_importance,
            order_by_key=False,
            reverse=True
        )
        return dual_result

    def _instance_dual(self, instance: Text, filter_zeros: bool = True) -> Optional[Dict]:
        # Getting global feature importance for tokens
        # present in the instance
        instance_vocab = bag_of_words(instances=instance)
        global_scores = self._global(vocabulary=instance_vocab)

        global_selection = feature_selection(
            global_scores=global_scores["global_scores_clipped"],
            ranking_length=self.ranking_length
        )
        if not global_selection:
            logger.warning("All features have a global feature "
                           "importance score of 0. DIME will not "
                           "be able to proceed with dual feature "
                           "importance calculation.")
            dual_scores = {}
            dual_normalized_scores = {}
            dual_probabilities = {}

        else:
            # Getting local feature importance for the
            # selected tokens in the instance
            dual_scores = self._dual(
                data_instance=instance,
                feature_set=global_selection,
                filter_zeros=filter_zeros
            )
            if dual_scores:
                dual_scores_clipped = clip_negative_values(vector=dual_scores['dual_importance_scores'])
                dual_normalized_scores = min_max_normalize(vector=dual_scores_clipped)
                dual_probabilities = to_probability_series(series=dual_scores['dual_importance_scores'])
            else:
                dual_normalized_scores = {}
                dual_probabilities = {}

        output_dict = {
            'global_scores': global_scores["global_scores_clipped"],
            'global_selection': global_selection,
            'global_normalized_scores': global_scores["global_normalized_scores"],
            'global_probabilities': global_scores["global_probabilities"],
            'dual_scores': dual_scores['dual_importance_scores'] if dual_scores else {},
            'predicted_intent': dual_scores['predicted_intent'] if dual_scores else "Failed to predict due to zero "
                                                                                    "feature selection",
            'predicted_confidence': dual_scores['predicted_confidence'] if dual_scores else 0.0,
            'dual_normalized_scores': dual_normalized_scores,
            'dual_probabilities': dual_probabilities,
        }
        return output_dict

    def explain(self, persist: bool = True, inspect: bool = False) -> Optional[DIMEExplanation]:
        try:
            explanation = dict()
            explanation['timestamp'] = {'start': get_timestamp_str(sep="-"), 'end': 'unknown'}

            if self.output_mode == OUTPUT_MODE_GLOBAL:
                logger.info(f"Calculating global feature importance "
                            f"for all tokens in the dataset")

                testing_vocab = self.testing_data.get_vocabulary()
                global_scores = self._global(vocabulary=testing_vocab)

                explanation['global'] = {
                    'feature_importance': global_scores["global_scores_clipped"],
                    'normalized_scores': global_scores["global_normalized_scores"],
                    'probability_scores': global_scores["global_probabilities"],
                }

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
                            'normalized_scores': {},
                            'probability_scores': {},
                        },
                        'dual': {
                            'feature_importance': {},
                            'normalized_scores': {},
                            'probability_scores': {},
                        }
                    }

                    # Getting global and dual feature importance scores
                    # for tokens present in the instance
                    dual_output = self._instance_dual(instance=instance, filter_zeros=True)

                    instance_scores['global']['feature_importance'] = dual_output['global_scores']
                    instance_scores['global']['feature_selection'] = dual_output['global_selection']
                    instance_scores['global']['normalized_scores'] = dual_output['global_normalized_scores']
                    instance_scores['global']['probability_scores'] = dual_output['global_probabilities']
                    instance_scores['global']['predicted_intent'] = dual_output['predicted_intent']
                    instance_scores['global']['predicted_confidence'] = dual_output['predicted_confidence']
                    instance_scores['dual']['feature_importance'] = dual_output['dual_scores']
                    instance_scores['dual']['normalized_scores'] = dual_output['dual_normalized_scores']
                    instance_scores['dual']['probability_scores'] = dual_output['dual_probabilities']

                    all_dime_scores.append(instance_scores)
                explanation['dual'] = all_dime_scores

            explanation['timestamp']['end'] = get_timestamp_str(sep="-")

            explanation['config'] = {
                'case_sensitive': self.case_sensitive,
                'output_mode': self.output_mode,
                'ranking_length': self.ranking_length if self.output_mode in [OUTPUT_MODE_DUAL] else "-",
                'metric': self.metric if self.output_mode in [OUTPUT_MODE_GLOBAL, OUTPUT_MODE_DUAL] else "-",
                'ngrams': {'min_ngrams': self.min_ngrams, 'max_ngrams': self.max_ngrams} if self.ngrams else "-"
            }
            explanation['model'] = {
                'name': self.model_name if self.model_mode == MODEL_MODE_LOCAL else "-",
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
            explanation['filename'] = ""

            dime_explanation = DIMEExplanation(explanation=explanation)

            if inspect:
                dime_explanation.inspect()

            if persist:
                dime_explanation.persist()

            return dime_explanation
        except Exception as e:
            raise RasaExplainerException(e)
