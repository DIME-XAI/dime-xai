import logging
import os
import pathlib
import re
import sys
from collections import OrderedDict as OrderedDictColl
from datetime import datetime
from os import path
from typing import List, Optional, Text, OrderedDict, Dict, NoReturn, Union, Tuple
from uuid import uuid4

from rasa.shared.data import get_data_files, is_nlu_file
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
    DEFAULT_LATEST_TAG,
    DEFAULT_INIT_DEST_DIR_NAME,
)
from dime_xai.shared.exceptions.dime_io_exceptions import (
    YAMLFormatException,
    NLUFileNotFoundException,
    ModelNotFoundException,
    InvalidFileExtensionException,
    FileSizeInspectingException,
)

logger = logging.getLogger(__name__)


def _create_cache_dir(cache_data_dir: Text = DEFAULT_CACHE_PATH) -> bool:
    """
    Creates the DIME caching directory to
    store the data/ model fingerprints and
    calculated global feature importance
    scores

    Args:
        cache_data_dir: directory path where the cache directory
            should be created

    Returns:
        True if cache dir was created, else False
    """

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
    """
    Returns the list files available in a given
    directory path and its subdirectories. able
    to check extensions if the extensions are
    provided as a list

    Args:
        dir_path: path where to read the list of directories
        file_suffixes: list of file extensions to look for. if
            not provided, the method will output all the files
            available in the given destination directory

    Returns:
        list of files available, or None
    """

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
    """
    Returns all files and directories existing
    in the specified destination directory and
    subdirectories

    Args:
        dir_path: destination directory path where
            to get the list of files and directories

    Returns:
        list of files and directories available, or
            None
    """

    file_list_all = list()

    for (dir_path, dir_names, file_names) in os.walk(dir_path):
        file_list_all += [dir_ for dir_ in dir_names]
        file_list_all += [file for file in file_names]

    return file_list_all


def get_existing_toplevel_file_list(
        dir_path: Text = DEFAULT_DATA_PATH,
        exclude: List = None
) -> Optional[List]:
    """
    Returns the list files available in a given
    directory path but not subdirectories. able
    to ignore files if the provided as a list under
    exclude argument

    Args:
        dir_path: path where to read the list of directories
        exclude: list of file names to ignore

    Returns:
        list of files available except the files mentioned in
            exclude list, or None
    """

    files = os.listdir(dir_path)
    if exclude:
        files = list(set(files).difference(set(exclude)))
    return files


def get_dime_init_caches(
        dir_path: Text = DEFAULT_INIT_DEST_DIR_NAME,
) -> Optional[List]:
    """
    Returns all dime cache directories in a
    specified directory path

    Args:
        dir_path: path to retrieve the list of
            initial DIME cache directories and
            files

    Returns:
        list of initial DIME caching directories
        and files
    """
    return [cache_dir for cache_dir in os.listdir(dir_path)
            if str(cache_dir).startswith(".dime_init_")]


def get_timestamp_str(sep: Text = "-", uuid: bool = False) -> Text:
    """
    Generates a timestamped string and attaches a unique
    ID using UUID if specified and returns it

    Args:
        sep: seperator to separate date, time and uuid
        uuid: if True, a unique UUID will be attached
            at the end of the timestamped string
            generated

    Returns:
        timestamped string
    """
    if uuid:
        return datetime.now().strftime('%Y%m%d' + sep + '%H%M%S' + sep) \
               + str(uuid4())
    else:
        return datetime.now().strftime('%Y%m%d' + sep + '%H%M%S')


def dir_exists(dir_path: Text = None) -> bool:
    """
    Checks if the specified directory path exists

    Args:
        dir_path: path of the directory to check
            the existence

    Returns:
        True if path exists, else False
    """
    return path.exists(dir_path) and path.isdir(dir_path)


def file_exists(file_path: Text = None) -> bool:
    """
    Checks if the specified file path exists

    Args:
        file_path: path of the file to check
            the existence

    Returns:
        True if path exists, else False
    """
    return path.exists(file_path) and path.isfile(file_path)


def file_size(file_path: Union[Text, List], reverse: bool = False) -> Union[Dict, Tuple[float, Text]]:
    try:
        if isinstance(file_path, Text):
            size_in_bytes = os.path.getsize(file_path)
            if size_in_bytes >= 1000000000:
                size = size_in_bytes / 1000000000
                units = "GB"
            elif size_in_bytes >= 1000000:
                size = size_in_bytes / 1000000
                units = "MB"
            elif size_in_bytes >= 1000:
                size = size_in_bytes / 1000
                units = "KB"
            else:
                size = size_in_bytes
                units = "Bytes"
            return size, units
        else:
            if reverse:
                file_path.reverse()
            file_sizes_dict = {file: file_size(file_path=file) for file in file_path}
            return file_sizes_dict
    except Exception as e:
        raise FileSizeInspectingException(e)


def is_bot_root() -> bool:
    """
    Checks if DIME CLI is running inside a RASA
    bot root directory. Looks only for specific
    file and directory existence including RASA
    config.yml, domain.yml and data directory.
    File list requires to be updated as required

    Returns:
        True if the current root directory if it is
            a RASA bot root directory, else False

    """
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
    """
    Reads the content of a specified YAML file.

    Args:
        yaml_file: YAML file to read the content from
        encoding: encoding of the specified file
        mode: read mode
        yaml_version: version of the YAML file, 2.0 is
            preferred
        version_check: True if required to check the
            version, else False

    Returns:
        YAML file content as an ordered dictionary, or
            None
    """
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
    """
    Given the content of a YAML file, finds and returns
    the specified YAML collection.

    Args:
        yaml_content: content of a YAML file as an ordered
            dictionary
        yaml_collection_tag: tag of the collection to be
            read

    Returns:
        The YAML collection extracted out of the YAML content
            as an ordered dictionary
    """
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
    Receives a collection of already retrieved
    RASA NLU examples and cleans it. Returns a
    sanitized non-empty collection of nlu example
    sentences.

    Args:
        collection_content: input data as an ordered
            dictionary
        case_sensitive:  if True, reads all data as
            lowercase, or else preserves the case and
            reads the files as is

    Returns:
        sanitized NLU data as a dictionary which
            has the list of examples under 'examples'
            under the key 'intent'
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
    Converts a given list to a list that only contains
    unique elements. Eliminates duplicate elements by
    converting to a set and back to a list.

    Args:
        list_of_data: list of elements

    Returns:
        list containing only unique elements, or None
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
    Reads testing data from rasa NLU testing
    data YAML files and returns a single list
    of sanitized testing data examples

    Args:
        testing_data_dir: path of the directory where to look
            for RASA testing data
        file_ext: extension of the testing data files to look
            for specified as a list. default is YAML or YML
        case_sensitive: if True, reads all data as lowercase, or
            else preserves the case and reads the files as is

    Returns:
        testing data as a dictionary with 'intent' and list of
            'examples' under each 'intent' key

    Raises:
        InvalidFileExtensionException: when the extension of the
            provided file is not a valid YAML file
    """

    try:
        testing_data = dict()
        logger.debug("Initializing testing data")

        if file_exists(file_path=testing_data_dir):
            file_extension = os.path.splitext(testing_data_dir)[-1]
            if file_extension in YAML_EXTENSIONS:
                testing_data_files = [testing_data_dir]
            else:
                raise InvalidFileExtensionException("The specified file is not a valid "
                                                    "YAML file")
        else:
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
    """
    wraps inbound string instances with ASCII
    color codes and returns a colored string
    that can be printed on the terminals

    Args:
        text_content: string instance to wrap
        color: color code to be visible on
            terminals

    Returns:
        wrapped string with the specified color
            that is ready to be printed on a
            terminal
    """
    return color + str(text_content) + TermColor.END_C


def exit_dime(exit_code: Union[int, Text] = 1, error_message: Text = None) -> NoReturn:
    """
    Prints error or exception message and
    exits the DIME CLI

    Args:
        exit_code: exit code as an integer
        error_message: error or exception log to
            be printed prior to terminating the
            DIME CLI

    Returns:
        no return
    """

    if error_message:
        logger.error(error_message)
    sys.exit(exit_code)


def get_latest_model_name(models_path: Text) -> Text:
    """
    Finds all RASA models available in the model dir
    provided and selects the latest model using the
    timestamp. if no path is given, it uses the default
    RASA models dir to collect model names

    Args:
        models_path: path of the directory where to look
            for RASA models

    Returns:
        latest model name as a string
    """

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


def update_sys_path(path_to_add: Text) -> NoReturn:
    """
    Appends a given path to the list of system
    paths. Can utilize this method to resolve
    import conflicts if packages or modules are
    being ignored at runtime in a specific
    location

    Args:
        path_to_add: path of the directory that
            that should be added to the system
            path list

    Returns:
        no return
    """
    sys.path.insert(0, path_to_add)


def series_to_json_serializable(series: Union[Dict, List]):
    if isinstance(series, dict):
        return {k: float(v) for k, v in series.items()}
    elif isinstance(series, list):
        return [float(v) for v in series]


def testing_data_dir_exists(dir_path: Text) -> bool:
    if not os.path.exists(dir_path):
        return False

    data_list = get_data_files(paths=[dir_path], filter_predicate=is_nlu_file)
    if len(data_list) == 0:
        return False

    return True


def rasa_models_dir_exists(dir_path: Text) -> bool:
    if not os.path.exists(dir_path):
        return False

    models = _get_dir_file_list(dir_path=dir_path, file_suffixes=RASA_MODEL_EXTENSIONS)
    if len(models) == 0:
        return False

    return True


def rasa_model_exists(models_path: Text, model_name: Text) -> bool:
    if str(model_name).lower() == DEFAULT_LATEST_TAG:
        return True

    if not re.fullmatch(RASA_288_MODEL_REGEX, model_name):
        return False

    if file_exists(file_path=os.path.join(models_path, model_name)):
        return True
    return False
