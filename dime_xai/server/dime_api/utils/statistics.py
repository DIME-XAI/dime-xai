import logging
import os
import re
from typing import Optional, List, Dict

from dime_xai.shared.constants import (
    RASA_288_MODEL_REGEX,
    DEFAULT_PERSIST_PATH,
    EXPLANATION_FILE_REGEX
)
from dime_xai.utils.io import (
    get_existing_toplevel_file_list,
    file_size
)

logger = logging.getLogger(__name__)


def model_statistics(request_data: Dict, reverse: bool) -> Optional[List]:
    models_path = request_data['models_path']
    models_list = get_existing_toplevel_file_list(
        dir_path=models_path,
    )
    model_sizes = file_size(
        file_path=[
            os.path.join(models_path, model_)
            for model_
            in models_list
            if re.match(RASA_288_MODEL_REGEX, model_)
        ],
        reverse=True if reverse else False,
    )
    model_sizes_list = [
        {
            "name": os.path.basename(model_),
            "size": str(round(size[0], 2)) + " " + str(size[1]),
        }
        for model_, size in model_sizes.items()]
    return model_sizes_list


def explanation_statistics(reverse: bool) -> Optional[List]:
    explanations_path = DEFAULT_PERSIST_PATH
    explanations_list = get_existing_toplevel_file_list(
        dir_path=explanations_path
    )
    explanations_list = [
        file_
        for file_
        in explanations_list
        if re.match(EXPLANATION_FILE_REGEX, file_)
    ]
    if reverse:
        explanations_list.reverse()
    return explanations_list
