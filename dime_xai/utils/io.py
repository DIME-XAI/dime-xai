import logging
import os
import re
import sys
from datetime import datetime
from os import path
import pathlib
from collections import OrderedDict as OrderedDictColl
from typing import List, Optional, Text, OrderedDict, Dict, NoReturn
from uuid import uuid4
from ruamel import yaml as yaml
from ruamel.yaml.error import YAMLError

from dime_xai.shared.constants import (
    DEFAULT_CACHE_PATH,
    DEFAULT_DATA_PATH,
    DEFAULT_NLU_YAML_TAG,
    DEFAULT_NLU_YAML_VERSION,
    DEFAULT_VERSION_YAML_TAG,
    YAML_EXTENSIONS,
    FILE_READ_PERMISSION,
    FILE_ENCODING_UTF8,
    DEFAULT_NLU_INTENT_TAG,
    DEFAULT_NLU_EXAMPLES_TAG,
    TermColor,
    RASA_MODEL_EXTENSIONS,
    RASA_288_MODEL_REGEX,
    DEFAULT_CASE_SENSITIVE_MODE,
)
from dime_xai.shared.exceptions.dime_io_exceptions import (
    YAMLFormatException,
    NLUFileNotFoundException,
    ModelNotFoundException,
)

logger = logging.getLogger(__name__)


def _create_cache_dir(cache_data_dir: Text = DEFAULT_CACHE_PATH) -> bool:
    if not cache_data_dir:
        logger.error("Cache dir not specified. dime will use the default caching directory to store the cached files.")
        cache_data_dir = DEFAULT_CACHE_PATH

    if not dir_exists(cache_data_dir):
        logger.warning("Could not find the default caching directory. a new cache will be created.")
        os.mkdir(cache_data_dir)

    return dir_exists(cache_data_dir)


def _get_dir_file_list(
        dir_path: Text = DEFAULT_DATA_PATH,
        file_suffixes: List = YAML_EXTENSIONS
) -> Optional[List]:
    file_paths = list()

    for (dir_path, dir_names, file_names) in os.walk(dir_path):
        if file_suffixes:
            file_paths += [path.join(dir_path, file) for file in file_names if str(file).endswith(tuple(file_suffixes))]
        else:
            file_paths += [path.join(dir_path, file) for file in file_names]
    return file_paths


def get_all_existing_file_list(
        dir_path: Text = DEFAULT_DATA_PATH,
) -> Optional[List]:
    file_list_all = list()

    for (dir_path, dir_names, file_names) in os.walk(dir_path):
        file_list_all += [dir_ for dir_ in dir_names]
        file_list_all += [file for file in file_names]

    return file_list_all


def get_existing_toplevel_file_list(
        dir_path: Text = DEFAULT_DATA_PATH,
        exclude: List = None
) -> Optional[List]:
    files = os.listdir(dir_path)
    if exclude:
        files = list(set(files).difference(set(exclude)))
    return files


def get_dime_init_caches(
        dir_path: Text = DEFAULT_DATA_PATH,
) -> Optional[List]:
    return [cache_dir for cache_dir in os.listdir(dir_path) if str(cache_dir).startswith(".dime_init_")]


def get_timestamp_str(sep: Text = "-", uuid: bool = False) -> Text:
    if uuid:
        return datetime.now().strftime('%Y%m%d' + sep + '%H%M%S' + sep) + str(uuid4())
    else:
        return datetime.now().strftime('%Y%m%d' + sep + '%H%M%S')


def dir_exists(dir_path: Text = None) -> bool:
    return path.exists(dir_path) and path.isdir(dir_path)


def file_exists(file_path: Text = None) -> bool:
    return path.exists(file_path) and path.isfile(file_path)


def is_bot_root() -> bool:  # TODO: edit as per the need
    bot_file_paths = list(pathlib.Path().glob("domain.yml"))
    bot_file_paths.append(list(pathlib.Path().glob("data")))
    bot_file_paths.append(list(pathlib.Path().glob("config.yml")))

    if len(bot_file_paths) == 3:
        return True
    else:
        return False


def read_yaml_file(
        yaml_file: Text = None,
        encoding: Text = FILE_ENCODING_UTF8,
        mode: Text = FILE_READ_PERMISSION,
        yaml_version: Text = DEFAULT_NLU_YAML_VERSION,
        version_check: bool = True,
) -> Optional[OrderedDict]:
    if not yaml_file:
        return OrderedDictColl()

    with open(file=yaml_file, encoding=encoding, mode=mode) as file_stream:
        try:
            yaml_content = yaml.round_trip_load(file_stream, preserve_quotes=False)
        except YAMLError as e:
            raise YAMLFormatException(e)

    if not yaml_content:
        return None

    if version_check:
        if DEFAULT_VERSION_YAML_TAG not in yaml_content:
            logger.debug("The YAML file is not properly versioned. the expected version is 2.0")
        else:
            if yaml_content[DEFAULT_VERSION_YAML_TAG] != yaml_version:
                logger.debug("The YAML file does not contain the expected rasa YAML version. the expected version is "
                             "2.0")

    return yaml_content


def _find_yaml_collection(
        yaml_content: OrderedDict = None,
        yaml_collection_tag: Text = DEFAULT_NLU_YAML_TAG,
) -> OrderedDict:
    if yaml_content is None:
        return OrderedDictColl()
    if yaml_collection_tag not in yaml_content:
        return OrderedDictColl()
    return yaml_content[yaml_collection_tag]


def _sanitize_nlu_data(
        collection_content: Optional[OrderedDict],
        case_sensitive: bool = DEFAULT_CASE_SENSITIVE_MODE
) -> Optional[Dict]:
    """
    receives a collection of already retrieved rasa nlu examples and cleans it.
    returns a sanitized non-empty collection of nlu example sentences.
    """
    if not collection_content:
        return None

    nlu_examples = {
        intent[DEFAULT_NLU_INTENT_TAG]: [
            str.strip(instance) for instance in
            (str.split(
                re.sub("- ", "", intent[DEFAULT_NLU_EXAMPLES_TAG]),
                "\n"
            ))
            if str.strip(instance) not in ['']
        ]
        for intent in collection_content
        if len(intent) == 2
    }

    if not case_sensitive:
        nlu_examples = {
            intent: [str.lower(example) for example in examples]
            for intent, examples
            in nlu_examples.items()
        }
    return nlu_examples


def get_unique_list(list_of_data: Optional[List] = None) -> Optional[List]:
    """
    converts a given list to a list that only contains unique elements.
    eliminates duplicates by converting to a set and back to a list.
    """
    if not list_of_data:
        return None
    return list(set(list_of_data))


def get_rasa_testing_data(
        testing_data_dir: Text = DEFAULT_DATA_PATH,
        file_ext: List = YAML_EXTENSIONS,
        case_sensitive: bool = DEFAULT_CASE_SENSITIVE_MODE
) -> Optional[Dict]:
    """
    reads testing data from rasa nlu testing data YAML files
    and returns single list of sanitized testing data examples.
    """

    try:
        testing_data = dict()
        logger.debug("Initializing testing data")

        # TODO: Implement a single file identification
        #  logic to identify single yml file paths
        testing_data_files = _get_dir_file_list(dir_path=testing_data_dir, file_suffixes=file_ext)
        logger.info(f"{len(testing_data_files)} YAML files were found in the testing data directory.")

        if testing_data_files:
            logger.debug(f"List of files found: {', '.join([os.path.split(fp)[-1] for fp in testing_data_files])}")

        for file in testing_data_files:
            try:
                nlu_data = read_yaml_file(
                    yaml_file=file,
                    version_check=True
                )
            except FileNotFoundError:
                raise NLUFileNotFoundException("Could not locate one or more NLU testing data YAML files")
            nlu_content = _find_yaml_collection(
                yaml_content=nlu_data,
                yaml_collection_tag=DEFAULT_NLU_YAML_TAG
            )
            cleaned_nlu_content = _sanitize_nlu_data(
                collection_content=nlu_content,
                case_sensitive=case_sensitive
            )

            if not cleaned_nlu_content:
                continue

            for intent, examples in cleaned_nlu_content.items():
                if intent in testing_data:
                    testing_data[intent] += examples
                else:
                    testing_data[intent] = examples

        return testing_data
    except NLUFileNotFoundException as e:
        logger.error(e)
    except YAMLFormatException as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)


def set_cli_color(text_content: Text = None, color: str = TermColor.NONE_C):
    return color + str(text_content) + TermColor.END_C


def exit_dime(exit_code: int = 1, error_message: Text = None) -> NoReturn:
    """Print error message and exit the application."""

    if error_message:
        logger.error(error_message)
    sys.exit(exit_code)


def get_latest_model_name(models_path: Text) -> Text:
    """ finds all models available in the model dir provided and selects the latest model using the timestamp. if no
    path is given, it uses the rasa default model dir to collect model names """

    model_list = _get_dir_file_list(
        dir_path=models_path,
        file_suffixes=RASA_MODEL_EXTENSIONS,
    )
    if not model_list:
        raise ModelNotFoundException(f"Could not find a compatible RASA model in the specified "
                                     f"location. Make sure there is a valid RASA model in "
                                     f"`{models_path}`")

    models_dict = {
        os.path.split(model_path)[-1]:
            int(''.join(list(re.findall(RASA_288_MODEL_REGEX, os.path.split(model_path)[-1])[0])))
        for model_path in model_list
        if re.findall(RASA_288_MODEL_REGEX, os.path.split(model_path)[-1])
    }

    latest_model = None
    max_timestamp = 0

    for model_name, timestamp in models_dict.items():
        if timestamp > max_timestamp:
            max_timestamp = timestamp
            latest_model = model_name

    logger.debug(f"Latest model found: {latest_model}")
    return latest_model


def update_sys_path(path_to_add: Text):
    sys.path.insert(0, path_to_add)
