import logging
from typing import Optional, List, Dict, Text, Union

import numpy as np
from sklearn.metrics import (
    f1_score,
    accuracy_score,
)

from dime_xai.shared.constants import (
    Metrics,
    Smoothing,
    DEFAULT_RANKING_LENGTH,
    NLU_FALLBACK_TAG,
)
from dime_xai.shared.explanation import DIMEExplanation
from dime_xai.shared.exceptions.dime_core_exceptions import (
    InvalidMetricSpecifiedException,
    InvalidIntentRankingException,
    InvalidNLUTagException,
    EmptyIntentRankingException,
)
from dime_xai.utils.io import series_to_json_serializable

logger = logging.getLogger(__name__)


def get_global_f1_score(
        model_output: List,
        average: Text = Metrics.AVG_WEIGHTED
) -> float:
    true_labels = [output['intent'] for output in model_output]
    predicted_labels = [output['predicted_intent'] for output in model_output]
    score = f1_score(
        y_true=true_labels,
        y_pred=predicted_labels,
        average=average
    )
    return score


def get_global_accuracy_score(
        model_output: List,
        normalize: bool = Metrics.AVG_WEIGHTED
) -> float:
    true_labels = [output['intent'] for output in model_output]
    predicted_labels = [output['predicted_intent'] for output in model_output]
    score = accuracy_score(
        y_true=true_labels,
        y_pred=predicted_labels,
        normalize=normalize
    )
    return score


def get_local_confidence_score(
        init_instance_output: Dict,
        token_instance_output: Dict,
) -> float:
    predicted_class = init_instance_output['predicted_intent']
    init_confidence = init_instance_output['predicted_confidence']

    if token_instance_output['predicted_intent'] == predicted_class:
        token_confidence = token_instance_output['predicted_confidence']
    elif predicted_class == NLU_FALLBACK_TAG or \
            token_instance_output['predicted_intent'] == NLU_FALLBACK_TAG:
        token_confidence = 0.0
    else:
        try:
            token_confidence = [i['confidence'] for i
                                in token_instance_output['intent_ranking']
                                if i['name'] == predicted_class][0]
        except IndexError:
            raise InvalidIntentRankingException(f"The predicted intent is not "
                                                f"available in the intent ranking list")
    token_confidence_diff = init_confidence - token_confidence
    return token_confidence_diff


def get_global_confidence_score(
        init_instance_output: Dict,
        token_instance_output: Dict,
) -> float:
    intent_confidence = init_instance_output['intent_confidence']
    predicted_intent_confidence = token_instance_output['intent_confidence']

    token_confidence_diff = intent_confidence - predicted_intent_confidence
    return token_confidence_diff


def get_global_score(
        token: Text,
        init_model_output: List,
        token_model_output: List,
        scorer: Text = Metrics.DEFAULT,
        average: Text = Metrics.AVG_WEIGHTED,
        normalize: bool = Metrics.NORMALIZE,
) -> Optional[float]:
    if scorer == Metrics.F1_SCORE:
        logger.warning("F1 Score metric is deprecated and will be removed in DIME XAI 2.0.0 "
                       "onwards. Use Modal Confidence instead.")
        init_f1_score = get_global_f1_score(model_output=init_model_output, average=average)
        token_f1_score = get_global_f1_score(model_output=token_model_output, average=average)

        if init_f1_score < token_f1_score:
            logger.warning(f"F1-Score has boosted for the token '{token}")
        token_f1_score_diff = init_f1_score - token_f1_score
        return token_f1_score_diff

    elif scorer == Metrics.ACCURACY:
        logger.warning("Accuracy metric is deprecated and will be removed in DIME XAI 2.0.0 "
                       "onwards. Use Modal Confidence instead.")
        init_accuracy = get_global_accuracy_score(model_output=init_model_output, normalize=normalize)
        token_accuracy = get_global_accuracy_score(model_output=token_model_output, normalize=normalize)

        if init_accuracy < token_accuracy:
            logger.info(f"Accuracy has boosted for the token '{token}")
        token_accuracy_diff = init_accuracy - token_accuracy
        return token_accuracy_diff

    elif scorer == Metrics.CONFIDENCE:
        token_confidence_diff = 0
        for init_instance in init_model_output:
            tag = init_instance['tag']
            token_instance = [x for x in token_model_output if x['tag'] == tag][0]

            if not token_instance:
                raise InvalidNLUTagException(f"There is a mismatch between NLU tags")

            # if 'intent_ranking' not in init_instance or \
            #         'intent_ranking' not in token_instance:
            #     raise EmptyIntentRankingException(f"Failed to retrieve the intent ranking")
            instance_confidence_score = get_global_confidence_score(
                init_instance_output=init_instance,
                token_instance_output=token_instance,
            )
            token_confidence_diff += instance_confidence_score
        return token_confidence_diff
    else:
        raise InvalidMetricSpecifiedException(f"The metric must be Accuracy, F1-Score, "
                                              f"or Confidence for Global feature importance")


def global_feature_importance(
        init_model_output: List,
        token_model_output: List,
        token: Text,
        scorer: Text = Metrics.CONFIDENCE,
        average: Text = Metrics.AVG_WEIGHTED,
        normalize: bool = Metrics.NORMALIZE,
) -> Optional[Dict]:
    score = get_global_score(
        init_model_output=init_model_output,
        token_model_output=token_model_output,
        scorer=scorer,
        average=average,
        normalize=normalize,
        token=token,
    )
    return score


def dual_feature_importance(
        init_instance_output: Dict,
        token_instance_output: Dict,
        scorer: Text = Metrics.CONFIDENCE,
) -> Optional[float]:
    if scorer in [Metrics.CONFIDENCE]:
        if 'intent_ranking' not in init_instance_output or \
                'intent_ranking' not in token_instance_output:
            raise EmptyIntentRankingException(f"Failed to retrieve the intent ranking")

        score = get_local_confidence_score(
            init_instance_output=init_instance_output,
            token_instance_output=token_instance_output,
        )
        return score
    else:
        logger.error("Dual Feature Importance requires Model Confidence as the metric by default. "
                     "Accuracy and F1-Score are only supported by Global feature importance only.")
        raise InvalidMetricSpecifiedException(f"The metric must be Model Confidence"
                                              f" for Dual feature importance")


def softmax(
        vector: Union[List, Dict]
) -> Union[np.array, Dict]:
    logger.warning("Softmax function 'softmax' is deprecated and will be removed in "
                   "DIME XAI 2.0.0 onwards. Use 'to_probability_series' instead.")
    if isinstance(vector, Dict):
        keys = list(vector.keys())
        values = list(vector.values())
        softmax_values = softmax(vector=values)
        softmax_dict = {keys[x]: softmax_values[x] for x in range(len(keys))}
        return series_to_json_serializable(softmax_dict)
    else:
        vector_copy = vector.copy()
        vector_np = np.array(vector_copy)
        return np.exp(vector_np) / np.exp(vector_np).sum()


def exp_norm_softmax(
        vector: Union[List, Dict]
) -> Union[np.array, Dict]:
    logger.warning("Normalized Exponential Softmax function 'exp_norm_softmax' is deprecated and "
                   "will be removed in DIME XAI 2.0.0 onwards. Use 'to_probability_series' instead.")
    if isinstance(vector, Dict):
        keys = list(vector.keys())
        values = list(vector.values())
        softmax_values = softmax(vector=values)
        softmax_dict = {keys[x]: softmax_values[x] for x in range(len(keys))}
        return series_to_json_serializable(softmax_dict)
    else:
        vector_copy = vector.copy()
        vector_np = np.array(vector_copy)
        b = max(vector_np)
        return np.exp(vector_np - b) / np.exp(vector_np - b).sum()


def clip_negative_values(
       vector: Union[List, Dict]
) -> Union[np.array, Dict]:
    if isinstance(vector, Dict):
        keys = list(vector.keys())
        values = list(vector.values())
        clipped_values = clip_negative_values(values)
        clipped_series = dict(zip(keys, clipped_values))
        return series_to_json_serializable(clipped_series)
    else:
        vector_copy = vector.copy()
        vector_np = np.array(vector_copy)
        vector_max = max(vector_np)
        vector_max = vector_max if vector_max > 0 else 0
        vector_np = np.clip(vector_np, a_min=0, a_max=vector_max)
        return vector_np


def min_max_normalize(
        vector: Union[List, Dict],
        min_value: int = 0,
) -> Union[np.array, Dict]:
    if isinstance(vector, Dict):
        keys = list(vector.keys())
        values = list(vector.values())
        normalized_values = min_max_normalize(vector=values, min_value=min_value)
        normalized_dict = {keys[x]: normalized_values[x] for x in range(len(keys))}
        return series_to_json_serializable(normalized_dict)
    else:
        vector_copy = vector.copy()
        vector_np = np.array(vector_copy)
        max_value = max(vector_np)
        vector_np = np.clip(vector_np, a_min=0, a_max=max_value)
        return (vector_np - min_value) / (max_value - min_value) \
            if (max_value - min_value) != 0 \
            else (vector_np - min_value)


def to_probability_series(
        series: Union[List, Dict]
) -> Union[np.array, Dict]:
    if isinstance(series, Dict):
        keys = list(series.keys())
        values = list(series.values())
        probabilities = to_probability_series(series=values)
        probabilities_dict = {keys[x]: probabilities[x] for x in range(len(keys))}
        return series_to_json_serializable(probabilities_dict)
    else:
        series_copy = series.copy()
        series_np = np.array(series_copy)
        series_max = max(series_np)
        series_np = np.clip(series_np, a_min=0, a_max=series_max)
        return series_np / series_np.sum() \
            if series_np.sum() != 0 \
            else series_np


def feature_selection(
        global_scores: Dict,
        ranking_length: int = DEFAULT_RANKING_LENGTH,
) -> Optional[Dict]:
    ranked_tokens = {
        t: s for t, s in sorted(
            global_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
    }

    selected_tokens = dict(zip(
        list(ranked_tokens.keys())[0:ranking_length],
        list(ranked_tokens.values())[0:ranking_length],
    ))

    non_zero_tokens = {
        k: v for k, v in selected_tokens.items()
        if v > 0
    }
    return non_zero_tokens


def apply_smoothing(
        vector: Union[List, Dict],
        smoothing_algorithm: Text = Smoothing.LAPLACE,
        smoothing_value: int = 1
) -> Union[List, Dict]:
    vector_copy = vector.copy()
    if isinstance(vector_copy, Dict):
        tokens = list(vector_copy.keys())
        values = list(vector_copy.values())
        smoothed_values = apply_smoothing(
            vector=values,
            smoothing_algorithm=smoothing_algorithm,
            smoothing_value=smoothing_value
        )
        return dict(zip(tokens, smoothed_values))
    else:
        if smoothing_algorithm == Smoothing.LAPLACE:
            return [value + smoothing_value for value in vector]


def load_explanation(explanation: Text) -> DIMEExplanation:
    dime_explanation = DIMEExplanation(explanation=explanation)
    return dime_explanation
