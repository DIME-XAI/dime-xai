import logging
from typing import Optional, List, Dict, Text, Union

import numpy as np
from sklearn.metrics import f1_score, accuracy_score

from dime_xai.shared.constants import Metrics, Smoothing, DEFAULT_RANKING_LENGTH
from dime_xai.shared.explanation import DIMEExplanation

logger = logging.getLogger(__name__)


def get_f1_score(
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


def get_accuracy_score(
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


def get_confidence_score(
        model_output: List,
        confidence_op: Text = Metrics.TOTAL_CONFIDENCE
) -> float:
    predicted_confidence = [output['intent_confidence'] for output in model_output]
    if confidence_op == Metrics.TOTAL_CONFIDENCE:
        total_predicted_confidence = sum(predicted_confidence)
        score = total_predicted_confidence
    elif confidence_op == Metrics.AVG_CONFIDENCE:
        average_predicted_confidence = sum(predicted_confidence) / len(predicted_confidence)
        score = average_predicted_confidence
    else:
        score = 0.0
    return score


def get_score(
        token: Text,
        init_model_output: List,
        token_model_output: List,
        scorer: Text = Metrics.DEFAULT,
        average: Text = Metrics.AVG_WEIGHTED,
        normalize: bool = Metrics.NORMALIZE,
        confidence_op: Text = Metrics.TOTAL_CONFIDENCE,
) -> Optional[float]:
    if scorer == Metrics.F1_SCORE:
        init_f1_score = get_f1_score(model_output=init_model_output, average=average)
        token_f1_score = get_f1_score(model_output=token_model_output, average=average)

        if init_f1_score < token_f1_score:
            logger.warning(f"F1-Score has boosted for the token '{token}")
        token_f1_score_diff = init_f1_score - token_f1_score
        return token_f1_score_diff

    elif scorer == Metrics.ACCURACY:
        init_accuracy = get_accuracy_score(model_output=init_model_output, normalize=normalize)
        token_accuracy = get_accuracy_score(model_output=token_model_output, normalize=normalize)

        if init_accuracy < token_accuracy:
            logger.info(f"Accuracy has boosted for the token '{token}")
        token_accuracy_diff = init_accuracy - token_accuracy
        return token_accuracy_diff

    elif scorer == Metrics.CONFIDENCE:
        init_confidence = get_confidence_score(model_output=init_model_output, confidence_op=confidence_op)
        token_confidence = get_confidence_score(model_output=token_model_output, confidence_op=confidence_op)

        if init_confidence < token_confidence:
            if confidence_op == Metrics.TOTAL_CONFIDENCE:
                logger.info(f"Total confidence has boosted for the token '{token}")
            if confidence_op == Metrics.AVG_CONFIDENCE:
                logger.info(f"Average confidence has boosted for the token '{token}")
        token_confidence_diff = init_confidence - token_confidence
        return token_confidence_diff


def softmax(
        vector: Union[List, Dict]
) -> Union[np.array, Dict]:
    if isinstance(vector, Dict):
        keys = list(vector.keys())
        values = list(vector.values())
        softmax_values = softmax(vector=values)
        return {keys[x]: softmax_values[x] for x in range(len(keys))}
    else:
        vector_copy = vector.copy()
        vector_np = np.array(vector_copy)
        return np.exp(vector_np) / np.exp(vector_np).sum()


def exp_norm_softmax(
        vector: Union[List, Dict]
) -> Union[np.array, Dict]:
    if isinstance(vector, Dict):
        keys = list(vector.keys())
        values = list(vector.values())
        softmax_values = softmax(vector=values)
        return {keys[x]: softmax_values[x] for x in range(len(keys))}
    else:
        vector_copy = vector.copy()
        vector_np = np.array(vector_copy)
        b = max(vector_np)
        return np.exp(vector_np - b) / np.exp(vector_np - b).sum()


def min_max_normalize(
        vector: Union[List, Dict],
        min_value: int = 0,
) -> Union[np.array, Dict]:
    if isinstance(vector, Dict):
        keys = list(vector.keys())
        values = list(vector.values())
        normalized_values = min_max_normalize(vector=values, min_value=min_value)
        return {keys[x]: normalized_values[x] for x in range(len(keys))}
    else:
        vector_copy = vector.copy()
        vector_np = np.array(vector_copy)
        max_value = max(vector_np)
        vector_np = np.clip(vector_np, a_min=0, a_max=max_value)
        return (vector_np - min_value) / (max_value - min_value)


def global_feature_importance(
        init_model_output: List,
        token_model_output: List,
        token: Text,
        scorer: Text = Metrics.F1_SCORE,
        average: Text = Metrics.AVG_WEIGHTED,
        normalize: bool = Metrics.NORMALIZE,
        confidence_op: Text = Metrics.TOTAL_CONFIDENCE,
) -> Optional[Dict]:
    score = get_score(
        init_model_output=init_model_output,
        token_model_output=token_model_output,
        scorer=scorer,
        average=average,
        normalize=normalize,
        confidence_op=confidence_op,
        token=token
    )
    return score


def local_feature_importance(
        selected_tokens: List,
) -> Optional[Dict]:
    # TODO :implement local
    return {'sample1': 2.5, 'sample2': 2}


def dual_feature_importance(
        global_selection: Dict,
        local_scores: Dict,
) -> Optional[Dict]:
    # TODO :implement dual
    return {'sample1': 2.5, 'sample2': 2}


def feature_selection(
        global_scores: Dict,
        ranking_length: int = DEFAULT_RANKING_LENGTH
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

    return selected_tokens


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
