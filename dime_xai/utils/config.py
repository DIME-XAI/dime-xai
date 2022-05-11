from typing import Optional, Dict, Text
import logging
import os
from collections import OrderedDict as OrderedDictColl

from dime_xai.shared.constants import (
    DEFAULT_CONFIG_FILE_PATH,
    DIMEConfig,
    InterfaceType,
    MODEL_TYPE_DIET,
    MODEL_TYPE_OTHER,
    MODEL_MODE_REST,
    MODEL_MODE_LOCAL,
    DEFAULT_RANKING_LENGTH,
    DEFAULT_MAX_NGRAMS,
    OUTPUT_MODE_LOCAL,
    OUTPUT_MODE_DUAL,
    OUTPUT_MODE_GLOBAL,
    LANGUAGES_SUPPORTED,
    DEFAULT_LATEST_TAG,
    FILE_ENCODING_UTF8,
    FILE_READ_PERMISSION,
    RASA_MODEL_EXTENSIONS,
    Metrics,
    ALLOWED_RASA_VERSIONS
)
from dime_xai.shared.exceptions.dime_io_exceptions import (
    DIMEConfigException,
    ConfigFileNotFoundException,
    InvalidMainKeyException,
    InvalidSubKeyException,
    InvalidDataTypeException,
    InvalidInterfaceException,
    InvalidConfigValueException,
    InvalidConfigPropertyException,
    MissingConfigPropertyException,
    InvalidPathSpecifiedException,
    InvalidURLSpecifiedException,
)
from dime_xai.utils.io import (
    read_yaml_file,
    dir_exists,
    file_exists,
    get_latest_model_name,
    exit_dime,
)
from dime_xai.shared.exceptions.dime_io_exceptions import (
    YAMLFormatException,
)

logger = logging.getLogger(__name__)


def get_default_configs(
        interface: Text = None,
        server_port: Text = None,
        data_instance: Text = None,
        output_mode: Text = None,
        global_metric: Text = None,
        case_sensitive: Text = None,
) -> Optional[Dict]:
    try:
        if not interface:
            interface = InterfaceType.INTERFACE_NONE

        if interface == InterfaceType.INTERFACE_NONE:
            logger.warning("An explicit interface has not been defined. "
                           "Any interface-related configs will not be "
                           "validated")
        elif interface == InterfaceType.INTERFACE_CLI:
            logger.debug("Interface has been set to 'CLI'. configs "
                         "related to SERVER will not be validated")
        elif interface == InterfaceType.INTERFACE_SERVER:
            logger.debug("Interface has been set to 'SERVER'. configs "
                         "related to CLI will not be validated")
        else:
            raise InvalidInterfaceException("An invalid interface has been "
                                            "specified. Please provide a valid "
                                            "interface name (CLI/SERVER)")

        try:
            yaml_content = read_yaml_file(
                yaml_file=DEFAULT_CONFIG_FILE_PATH,
                encoding=FILE_ENCODING_UTF8,
                mode=FILE_READ_PERMISSION,
            )
        except FileNotFoundError:
            raise ConfigFileNotFoundException("Could not locate the 'dime_config.yml' file. "
                                              "Make sure it is in the root directory")

        if not yaml_content:
            raise DIMEConfigException("The given 'dime_config.yml' file is empty")

        config_content = dict()
        all_keys = list()

        for key in yaml_content:
            if key not in DIMEConfig.MAIN_CONFIG_KEYS:
                raise InvalidMainKeyException(f"Invalid configuration key: '{key}'")

            all_keys.append(key)
            sub_keys = list()
            props = dict()

            # subkey validation
            for subkey in yaml_content[key]:
                if not isinstance(subkey, OrderedDictColl):
                    raise InvalidSubKeyException(f"Invalid config key was found: {subkey}")
                subkey_list = list(dict(subkey).keys())
                if subkey_list:
                    all_keys.append(subkey_list[0])
                    sub_keys.append(subkey_list[0])

                    if len(subkey_list) > 1:
                        props[subkey_list[0]] = subkey_list[1:]

            if None in sub_keys or sorted(sub_keys) != sorted(list(DIMEConfig.MAIN_CONFIG_KEYS[key])):
                missing_keys = set(DIMEConfig.MAIN_CONFIG_KEYS[key]).difference(set(sub_keys))
                invalid_keys = [invalid_key for invalid_key in
                                set(sub_keys).difference((DIMEConfig.MAIN_CONFIG_KEYS[key])) if invalid_key]
                raise InvalidSubKeyException(f"Required configs are either invalid or missing under '{key}' "
                                             f"key in the 'dime_config.yml' file. "
                                             f"\nMissing Keys: {', '.join(missing_keys)}"
                                             f"\nInvalid Keys: {', '.join(invalid_keys)}")

            # prop validation
            if props:
                for k, v in props.items():
                    if k in DIMEConfig.BASE_CONFIG_PROPS:
                        for prop in v:
                            if prop not in DIMEConfig.BASE_CONFIG_PROPS[k]:
                                raise InvalidConfigPropertyException(f"Invalid config property '{prop}' "
                                                                     f"specified under subkey '{k}'")
                    else:
                        raise InvalidConfigPropertyException(f"{k} does not allow specifying any properties")

                    props_diff = set(DIMEConfig.BASE_CONFIG_PROPS[k]).difference(set(v))
                    if props_diff:
                        raise MissingConfigPropertyException(f"Required properties are missing: "
                                                             f"{', '.join(props_diff)}")

            # individual subkey validation
            key_content_dict = {key: val for config in yaml_content[key] for (key, val) in dict(config).items()}

            if key == DIMEConfig.MAIN_KEY_BASE:
                # replacing configs with CLI arguments passed
                if data_instance:
                    logger.warning("The instances specified in the config file "
                                   f"will be discarded and set to instance specified "
                                   f"while running the DIME CLI")
                    key_content_dict[DIMEConfig.SUB_KEY_BASE_DATA_INSTANCE] = [data_instance]

                if global_metric:
                    logger.warning("The global metric specified in the config file "
                                   f"will be discarded and set to '{global_metric}'")
                    key_content_dict[DIMEConfig.SUB_KEY_BASE_GLOBAL_METRIC] = global_metric

                if case_sensitive in [True, False]:
                    logger.warning("The case sensitivity specified in the config file "
                                   f"will be discarded and set to '{case_sensitive}'")
                    key_content_dict[DIMEConfig.SUB_KEY_BASE_CASE_SENSITIVITY] = case_sensitive

                for s, c in key_content_dict.items():
                    if not c and s not in [DIMEConfig.SUB_KEY_BASE_MODEL_NAME,
                                           DIMEConfig.SUB_KEY_BASE_RANKING_LENGTH,
                                           DIMEConfig.SUB_KEY_BASE_NGRAMS,
                                           DIMEConfig.SUB_KEY_BASE_NGRAMS_MAX,
                                           DIMEConfig.SUB_KEY_BASE_NGRAMS_MIN,
                                           DIMEConfig.SUB_KEY_BASE_CASE_SENSITIVITY]:
                        raise InvalidConfigValueException(f"'{s}' of '{key}' cannot be empty")

                # TODO: Enable reading data instances from a file,
                #  possibly a yml
                if isinstance(key_content_dict[DIMEConfig.SUB_KEY_BASE_DATA_INSTANCE], str):
                    key_content_dict[DIMEConfig.SUB_KEY_BASE_DATA_INSTANCE] = \
                        [key_content_dict[DIMEConfig.SUB_KEY_BASE_DATA_INSTANCE]]

                if isinstance(key_content_dict[DIMEConfig.SUB_KEY_BASE_LANGUAGES], str):
                    key_content_dict[DIMEConfig.SUB_KEY_BASE_LANGUAGES] = \
                        [key_content_dict[DIMEConfig.SUB_KEY_BASE_LANGUAGES]]

                valid_instances = list()
                for instance in key_content_dict[DIMEConfig.SUB_KEY_BASE_DATA_INSTANCE]:
                    if instance:
                        valid_instances.append(instance)

                if not valid_instances:
                    raise InvalidConfigValueException(f"List of Data Instances provided are "
                                                      f"invalid. Please make sure to include "
                                                      f"at least one valid data instance in the "
                                                      f"'dime_config.yml' file")
                else:
                    key_content_dict[DIMEConfig.SUB_KEY_BASE_DATA_INSTANCE] = valid_instances

                invalid_languages = list()
                for lang in key_content_dict[DIMEConfig.SUB_KEY_BASE_LANGUAGES]:
                    if str.lower(lang) not in LANGUAGES_SUPPORTED:
                        invalid_languages.append(lang)
                if invalid_languages:
                    raise InvalidConfigValueException(f"Unsupported lang codes were found: "
                                                      f"{', '.join(invalid_languages)}")

                if not dir_exists(key_content_dict[DIMEConfig.SUB_KEY_BASE_DATA_PATH]) and \
                        not file_exists(key_content_dict[DIMEConfig.SUB_KEY_BASE_DATA_PATH]):
                    raise InvalidPathSpecifiedException(f"'{DIMEConfig.SUB_KEY_BASE_DATA_PATH}' specified in the "
                                                        f"config file must be a valid directory path")

                if not dir_exists(key_content_dict[DIMEConfig.SUB_KEY_BASE_MODELS_PATH]):
                    raise InvalidPathSpecifiedException(f"'{DIMEConfig.SUB_KEY_BASE_MODELS_PATH}' specified in the "
                                                        f"config file must be a valid directory path")

                if DIMEConfig.SUB_KEY_BASE_MODEL_NAME in key_content_dict:
                    if not key_content_dict[DIMEConfig.SUB_KEY_BASE_MODEL_NAME] or \
                            str.lower(key_content_dict[DIMEConfig.SUB_KEY_BASE_MODEL_NAME]) == 'none':
                        key_content_dict[DIMEConfig.SUB_KEY_BASE_MODEL_NAME] = DEFAULT_LATEST_TAG

                    if not isinstance(key_content_dict[DIMEConfig.SUB_KEY_BASE_MODEL_NAME], str):
                        raise InvalidDataTypeException(f"'{DIMEConfig.SUB_KEY_BASE_MODEL_NAME}' must be a String")

                    if str.lower(key_content_dict[DIMEConfig.SUB_KEY_BASE_MODEL_NAME]) != 'latest':
                        if not str(key_content_dict[DIMEConfig.SUB_KEY_BASE_MODEL_NAME]).endswith(
                                tuple(RASA_MODEL_EXTENSIONS)
                        ):
                            raise InvalidDataTypeException(f"'{DIMEConfig.SUB_KEY_BASE_MODEL_NAME}' must have a "
                                                           f"valid RASA model extension: "
                                                           f"{'. '.join(RASA_MODEL_EXTENSIONS)}")
                        else:
                            full_model_path = os.path.join(
                                key_content_dict[DIMEConfig.SUB_KEY_BASE_MODELS_PATH],
                                key_content_dict[DIMEConfig.SUB_KEY_BASE_MODEL_NAME]
                            )
                            if not file_exists(full_model_path):
                                raise InvalidPathSpecifiedException(
                                    f"'{key_content_dict[DIMEConfig.SUB_KEY_BASE_MODEL_NAME]}' does not exist in "
                                    f"models directory specified, "
                                    f"'{key_content_dict[DIMEConfig.SUB_KEY_BASE_MODELS_PATH]}'")
                else:
                    key_content_dict[DIMEConfig.SUB_KEY_BASE_MODEL_NAME] = DEFAULT_LATEST_TAG

                if key_content_dict[DIMEConfig.SUB_KEY_BASE_MODEL_NAME] == DEFAULT_LATEST_TAG:
                    key_content_dict[DIMEConfig.SUB_KEY_BASE_MODEL_NAME] = \
                        get_latest_model_name(models_path=key_content_dict[DIMEConfig.SUB_KEY_BASE_MODELS_PATH])

                if str.lower(key_content_dict[DIMEConfig.SUB_KEY_BASE_MODEL_TYPE]) not in \
                        [MODEL_TYPE_DIET, MODEL_TYPE_OTHER]:
                    raise InvalidConfigValueException(f"'{DIMEConfig.SUB_KEY_BASE_MODEL_TYPE}' must be either "
                                                      f"'{MODEL_TYPE_DIET}' or '{MODEL_TYPE_OTHER}'")

                if str.lower(key_content_dict[DIMEConfig.SUB_KEY_BASE_MODEL_TYPE]) == MODEL_TYPE_DIET:
                    if DIMEConfig.SUB_KEY_BASE_MODEL_TYPE not in props or \
                            DIMEConfig.SUB_KEY_BASE_RASA_VERSION not in props[DIMEConfig.SUB_KEY_BASE_MODEL_TYPE]:
                        raise MissingConfigPropertyException(f"RASA model version is missing from "
                                                             f"'{DIMEConfig.SUB_KEY_BASE_MODEL_TYPE}' "
                                                             f"in 'dime_config.yml'")

                    if key_content_dict[DIMEConfig.SUB_KEY_BASE_RASA_VERSION] \
                            not in ALLOWED_RASA_VERSIONS:
                        raise InvalidConfigValueException(f"RASA model version is not supported by the "
                                                          f"current implementation of DIME. Please make "
                                                          f"sure to use a 2.x.x RASA version")
                else:
                    logger.error(f"Model types other than RASA DIET are not yet supported by DIME. "
                                 f"Run DIME with a RASA model instead.")
                    exit_dime(1)

                if str.lower(key_content_dict[DIMEConfig.SUB_KEY_BASE_MODEL_MODE]) not in \
                        [MODEL_MODE_REST, MODEL_MODE_LOCAL]:
                    raise InvalidConfigValueException(f"'{DIMEConfig.SUB_KEY_BASE_MODEL_MODE}' must be either "
                                                      f"'{MODEL_MODE_REST}' or '{MODEL_MODE_LOCAL}'")

                if not isinstance(key_content_dict[DIMEConfig.SUB_KEY_BASE_RANKING_LENGTH], int):
                    raise InvalidConfigValueException(f"'{DIMEConfig.SUB_KEY_BASE_RANKING_LENGTH}' must be an Integer")

                if not 0 < key_content_dict[DIMEConfig.SUB_KEY_BASE_RANKING_LENGTH] <= DEFAULT_RANKING_LENGTH:
                    key_content_dict[DIMEConfig.SUB_KEY_BASE_RANKING_LENGTH] = DEFAULT_RANKING_LENGTH
                    raise InvalidConfigValueException(f"'{DIMEConfig.SUB_KEY_BASE_RANKING_LENGTH}' was set to "
                                                      f"{DEFAULT_RANKING_LENGTH}. "
                                                      f"'{DIMEConfig.SUB_KEY_BASE_RANKING_LENGTH}' must be a "
                                                      f"positive Integer not greater than "
                                                      f"{DEFAULT_RANKING_LENGTH}")

                if not isinstance(key_content_dict[DIMEConfig.SUB_KEY_BASE_NGRAMS], bool):
                    raise InvalidDataTypeException(f"'{DIMEConfig.SUB_KEY_BASE_NGRAMS}' must be either True or False")

                if key_content_dict[DIMEConfig.SUB_KEY_BASE_NGRAMS]:
                    if DIMEConfig.SUB_KEY_BASE_NGRAMS not in props or \
                            DIMEConfig.SUB_KEY_BASE_NGRAMS_MIN not in props[DIMEConfig.SUB_KEY_BASE_NGRAMS] or \
                            DIMEConfig.SUB_KEY_BASE_NGRAMS_MAX not in props[DIMEConfig.SUB_KEY_BASE_NGRAMS]:
                        raise MissingConfigPropertyException(f"Required properties "
                                                             f"'{DIMEConfig.SUB_KEY_BASE_NGRAMS_MIN}', "
                                                             f"'{DIMEConfig.SUB_KEY_BASE_NGRAMS_MAX}', or both "
                                                             f"are missing from '{DIMEConfig.SUB_KEY_BASE_NGRAMS}' "
                                                             f"in 'dime_config.yml'")

                    if not isinstance(key_content_dict[DIMEConfig.SUB_KEY_BASE_NGRAMS_MIN], int) or \
                            not isinstance(key_content_dict[DIMEConfig.SUB_KEY_BASE_NGRAMS_MAX], int):
                        raise InvalidDataTypeException(f"'{DIMEConfig.SUB_KEY_BASE_NGRAMS_MIN}' and "
                                                       f"{DIMEConfig.SUB_KEY_BASE_NGRAMS_MAX}' must be Integers")

                    if key_content_dict[DIMEConfig.SUB_KEY_BASE_NGRAMS_MIN] > \
                            key_content_dict[DIMEConfig.SUB_KEY_BASE_NGRAMS_MAX] or \
                            not 0 < key_content_dict[DIMEConfig.SUB_KEY_BASE_NGRAMS_MIN] <= DEFAULT_MAX_NGRAMS or \
                            not 0 < key_content_dict[DIMEConfig.SUB_KEY_BASE_NGRAMS_MAX] <= DEFAULT_MAX_NGRAMS:
                        raise InvalidConfigValueException(f"'{DIMEConfig.SUB_KEY_BASE_NGRAMS_MIN}' and "
                                                          f"'{DIMEConfig.SUB_KEY_BASE_NGRAMS_MAX}' should be positive "
                                                          f"Integers not lower than {DEFAULT_MAX_NGRAMS} and "
                                                          f"'{DIMEConfig.SUB_KEY_BASE_NGRAMS_MIN}' should not exceed "
                                                          f"'{DIMEConfig.SUB_KEY_BASE_NGRAMS_MAX}'")

                if not isinstance(key_content_dict[DIMEConfig.SUB_KEY_BASE_CASE_SENSITIVITY], bool):
                    raise InvalidDataTypeException(f"'{DIMEConfig.SUB_KEY_BASE_CASE_SENSITIVITY}' must be either True "
                                                   f"or False")

                if str.lower(key_content_dict[DIMEConfig.SUB_KEY_BASE_GLOBAL_METRIC]) not in \
                        [Metrics.F1_SCORE, Metrics.ACCURACY, Metrics.CONFIDENCE]:
                    raise InvalidConfigValueException(f"'{DIMEConfig.SUB_KEY_BASE_GLOBAL_METRIC}' must be either "
                                                      f"'{Metrics.F1_SCORE}', '{Metrics.CONFIDENCE}' or "
                                                      f"'{Metrics.ACCURACY}'")

            elif key == DIMEConfig.MAIN_KEY_SERVER and interface == InterfaceType.INTERFACE_SERVER:
                # replacing configs with CLI arguments passed
                if server_port:
                    logger.warning("The port specified in the config file "
                                   f"will be discarded and set to '{server_port}'")
                    key_content_dict[DIMEConfig.SUB_KEY_SERVER_PORT] = server_port

                for s, c in key_content_dict.items():
                    if not c:
                        raise InvalidConfigValueException(f"'{s}' of '{key}' cannot be empty")

                if not isinstance(key_content_dict[DIMEConfig.SUB_KEY_SERVER_PORT], int):
                    raise InvalidConfigValueException(f"'{DIMEConfig.SUB_KEY_SERVER_PORT}' must be an Integer that "
                                                      f"represents a valid port number")

            elif key == DIMEConfig.MAIN_KEY_CLI and interface == InterfaceType.INTERFACE_CLI:
                # replacing configs with CLI arguments passed
                if output_mode:
                    logger.warning(f"The CLI output mode specified in the "
                                   f"config file will be discarded and "
                                   f"set to '{output_mode}'")
                    key_content_dict[DIMEConfig.SUB_KEY_CLI_OUTPUT_MODE] = output_mode

                for s, c in key_content_dict.items():
                    if not c:
                        raise InvalidConfigValueException(f"'{s}' of '{key}' cannot be empty")

                if key_content_dict[DIMEConfig.SUB_KEY_CLI_OUTPUT_MODE] not in \
                        [OUTPUT_MODE_LOCAL, OUTPUT_MODE_GLOBAL, OUTPUT_MODE_DUAL]:
                    raise InvalidConfigValueException(f"'{DIMEConfig.SUB_KEY_CLI_OUTPUT_MODE}' must be "
                                                      f"'{OUTPUT_MODE_DUAL}', '{OUTPUT_MODE_LOCAL}', or "
                                                      f"'{OUTPUT_MODE_GLOBAL}")

                if key_content_dict[DIMEConfig.SUB_KEY_CLI_OUTPUT_MODE] == OUTPUT_MODE_GLOBAL:
                    logger.warning(f"DIME CLI output mode has been set to '{OUTPUT_MODE_GLOBAL}'."
                                   f"Any data instances specified will be discarded.")

            config_content[key] = key_content_dict

        # sanity check in main keys
        if not config_content:
            raise DIMEConfigException("Retrieved configurations are empty.")

        return config_content

    except ConfigFileNotFoundException as e:
        logger.error(f"{e}")
    except YAMLFormatException as e:
        logger.error(f"{e}")
    except InvalidMainKeyException as e:
        logger.error(f"{e}")
    except InvalidSubKeyException as e:
        logger.error(f"{e}")
    except InvalidDataTypeException as e:
        logger.error(f"{e}")
    except InvalidInterfaceException as e:
        logger.error(f"{e}")
    except InvalidConfigValueException as e:
        logger.error(f"{e}")
    except InvalidConfigPropertyException as e:
        logger.error(f"{e}")
    except InvalidPathSpecifiedException as e:
        logger.error(f"{e}")
    except InvalidURLSpecifiedException as e:
        logger.error(f"{e}")
    except DIMEConfigException or Exception as e:
        logger.error(f"{e}")
