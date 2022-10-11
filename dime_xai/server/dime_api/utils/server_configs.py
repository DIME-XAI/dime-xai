import json
import logging
import os
import re
from typing import Dict, NoReturn, Tuple, Text

import ruamel.yaml as yml

from dime_xai.shared.constants import (
    DEFAULT_CONFIG_FILE_PATH,
    DIMEConfig, 
    MODEL_MODE_LOCAL,
    MODEL_MODE_REST,
    BOT_URL_REGEX,
    BOT_URL_REGEX_HTTP,
    Validity,
    ServerConfigType,
    FilePermission,
    Encoding,
)
from dime_xai.shared.exceptions.dime_io_exceptions import (
    ConfigFileNotFoundException,
    DIMEConfigException,
)
from dime_xai.shared.exceptions.dime_server_exceptions import (
    InvalidServerConfigsException,
    ServerConfigsPersistException,
    InvalidConfigurationTypeSpecifiedException,
    CustomConfigsNotFoundException,
)
from dime_xai.utils.io import read_yaml_file
from dime_xai.utils.io import (
    testing_data_dir_exists,
    rasa_models_dir_exists,
    rasa_model_exists,
)

logger = logging.getLogger(__name__)


class ServerConfigs:
    def __init__(self):
        self.configs_yml = None
        try:
            self._initialize()
        except Exception as e:
            logger.error(f"Exception occurred while initializing server configs. {e}")
            raise InvalidServerConfigsException(e)

    def _initialize(self) -> NoReturn:
        try:
            yaml_content = read_yaml_file(
                yaml_file=DEFAULT_CONFIG_FILE_PATH,
                encoding=Encoding.UTF8,
                mode=FilePermission.READ,
                version_check=False,
            )
            self.configs_yml = yaml_content
            self.configs = json.loads(json.dumps(yaml_content, ensure_ascii=False))
            for key in self.configs.keys():
                key_content_dict = dict()
                for element_dict in self.configs[key]:
                    for element_key, element_value in element_dict.items():
                        key_content_dict[element_key] = element_value

                self.configs[key] = key_content_dict
        except FileNotFoundError:
            raise ConfigFileNotFoundException("Could not locate the 'dime_config.yml' file. "
                                              "Make sure it is in the root directory")
        except Exception as e:
            logger.error(f"Exception occurred while retrieving 'dime_config.yml'. {e}")
            raise DIMEConfigException(e)

    @staticmethod
    def validate(configs: Dict, secure_url: bool = True) -> Tuple[bool, Dict]:
        validate_status_obj = {
            "keys": Validity.NOTSET,
            DIMEConfig.SUB_KEY_BASE_DATA_PATH: Validity.NOTSET,
            DIMEConfig.SUB_KEY_BASE_MODELS_PATH: Validity.NOTSET,
            DIMEConfig.SUB_KEY_BASE_MODEL_NAME: Validity.NOTSET,
            DIMEConfig.SUB_KEY_BASE_MODEL_MODE: Validity.NOTSET,
            DIMEConfig.SUB_KEY_BASE_URL_ENDPOINT: Validity.NOTSET,
            DIMEConfig.SUB_KEY_BASE_RANKING_LENGTH: Validity.NOTSET,
            DIMEConfig.SUB_KEY_BASE_CASE_SENSITIVITY: Validity.NOTSET,
        }
        validate_status = False

        try:
            keys = list(configs)
            if sorted(keys) != sorted([
                DIMEConfig.SUB_KEY_BASE_DATA_PATH,
                DIMEConfig.SUB_KEY_BASE_MODELS_PATH,
                DIMEConfig.SUB_KEY_BASE_MODEL_NAME,
                DIMEConfig.SUB_KEY_BASE_MODEL_MODE,
                DIMEConfig.SUB_KEY_BASE_URL_ENDPOINT,
                DIMEConfig.SUB_KEY_BASE_RANKING_LENGTH,
                DIMEConfig.SUB_KEY_BASE_CASE_SENSITIVITY
            ]):
                logger.error("Failed to validate updated server config keys")
                validate_status_obj['keys'] = Validity.INVALID
            else:
                validate_status_obj['keys'] = Validity.VALID

            # model mode validation
            if configs[DIMEConfig.SUB_KEY_BASE_MODEL_MODE] \
                    not in [MODEL_MODE_LOCAL, MODEL_MODE_REST]:
                logger.error("Failed to validate model mode in updated server configs")
                validate_status_obj[DIMEConfig.SUB_KEY_BASE_MODEL_MODE] = Validity.INVALID
            else:
                validate_status_obj[DIMEConfig.SUB_KEY_BASE_MODEL_MODE] = Validity.VALID

            # data path validation
            if not testing_data_dir_exists(
                    dir_path=configs[DIMEConfig.SUB_KEY_BASE_DATA_PATH]
            ):
                logger.error("Failed to validate data path in updated server configs")
                validate_status_obj[DIMEConfig.SUB_KEY_BASE_DATA_PATH] = Validity.INVALID
            else:
                validate_status_obj[DIMEConfig.SUB_KEY_BASE_DATA_PATH] = Validity.VALID

            # models path validation
            if not rasa_models_dir_exists(
                    dir_path=configs[DIMEConfig.SUB_KEY_BASE_MODELS_PATH]
            ):
                logger.error("Failed to validate models path in updated server configs")
                validate_status_obj[DIMEConfig.SUB_KEY_BASE_MODELS_PATH] = Validity.INVALID
            else:
                validate_status_obj[DIMEConfig.SUB_KEY_BASE_MODELS_PATH] = Validity.VALID

            # model name validation
            if not rasa_model_exists(
                    models_path=configs[DIMEConfig.SUB_KEY_BASE_MODELS_PATH],
                    model_name=configs[DIMEConfig.SUB_KEY_BASE_MODEL_NAME],
            ):
                logger.error("Failed to validate model name in updated server configs")
                validate_status_obj[DIMEConfig.SUB_KEY_BASE_MODEL_NAME] = Validity.INVALID
            else:
                validate_status_obj[DIMEConfig.SUB_KEY_BASE_MODEL_NAME] = Validity.VALID

            # url endpoint validation
            bot_url_regex_ = BOT_URL_REGEX if secure_url else BOT_URL_REGEX_HTTP
            if not re.findall(
                bot_url_regex_,
                configs[DIMEConfig.SUB_KEY_BASE_URL_ENDPOINT]
            ):
                logger.error("Failed to validate url endpoint in updated server configs")
                validate_status_obj[DIMEConfig.SUB_KEY_BASE_URL_ENDPOINT] = Validity.INVALID
            else:

                validate_status_obj[DIMEConfig.SUB_KEY_BASE_URL_ENDPOINT] = Validity.VALID

            # ranking length validation
            if isinstance(configs[DIMEConfig.SUB_KEY_BASE_RANKING_LENGTH], int):
                if not 0 < configs[DIMEConfig.SUB_KEY_BASE_RANKING_LENGTH] <= 20:
                    logger.error("Failed to validate ranking length range in updated server configs")
                    validate_status_obj[DIMEConfig.SUB_KEY_BASE_RANKING_LENGTH] = Validity.INVALID
                else:
                    validate_status_obj[DIMEConfig.SUB_KEY_BASE_RANKING_LENGTH] = Validity.VALID
            else:
                logger.error("Failed to validate ranking length in updated server configs")
                validate_status_obj[DIMEConfig.SUB_KEY_BASE_RANKING_LENGTH] = Validity.INVALID

            # case sensitivity validation
            if configs[DIMEConfig.SUB_KEY_BASE_CASE_SENSITIVITY] \
                    not in [True, False]:
                logger.error("Failed to validate case sensitivity in updated server configs")
                validate_status_obj[DIMEConfig.SUB_KEY_BASE_CASE_SENSITIVITY] = Validity.INVALID
            else:
                validate_status_obj[DIMEConfig.SUB_KEY_BASE_CASE_SENSITIVITY] = Validity.VALID

            # check if all keys are valid
            if Validity.INVALID in validate_status_obj.values():
                validate_status = False
            else:
                validate_status = True
            return validate_status, validate_status_obj
        except Exception as e:
            logger.error(f"Exception occurred while validating server configurations. {e}")
            return validate_status, validate_status_obj

    def update_and_persist(self, updated_configs: Dict, validate: bool = True):
        try:
            # latest configs
            self._initialize()
            
            if validate:
                if not self.validate(updated_configs)[0]:
                    raise InvalidServerConfigsException()

            # handling sub keys
            models_path = updated_configs['models_path']
            model_name = str(updated_configs['model_name']).lower()
            del updated_configs['model_name']
            updated_configs['models_path'] = dict(models_path=models_path, model_name=model_name)

            dime_base_configs = self.configs_yml.get(DIMEConfig.MAIN_KEY_BASE)
            for k, v in updated_configs.items():
                for index, element in enumerate(dime_base_configs):
                    if k in dict(element).keys():
                        if k == 'models_path':
                            dime_base_configs[index] = v
                        else:
                            dime_base_configs[index] = {k: v}
            self.configs_yml[DIMEConfig.MAIN_KEY_BASE] = dime_base_configs

            # modifying the latest configs
            with open(
                    file=os.path.join(DEFAULT_CONFIG_FILE_PATH),
                    encoding=Encoding.UTF8,
                    mode=FilePermission.WRITE
            ) as server_configs:
                yaml = yml.YAML()
                yaml.indent(sequence=4, offset=2)
                yaml.dump(self.configs_yml, server_configs)

            # retrieve saved configs
            self._initialize()

            logger.debug("Saved server configs")
        except Exception as e:
            raise ServerConfigsPersistException(e)

    def retrieve(self, config_type: Text = ServerConfigType.JSON, custom_configs: bool = False) -> Text:
        if not config_type or config_type not in [ServerConfigType.JSON, ServerConfigType.NONE]:
            raise InvalidConfigurationTypeSpecifiedException()

        if custom_configs:
            try:
                keyboard_enabled = bool(os.environ.get("KEYBOARD_ENABLED"))
                app_env = os.environ.get("APP_ENV")
                app_theme = os.environ.get("APP_THEME")
                self.configs["custom_configs"] = {
                    "keyboard_enabled": keyboard_enabled,
                    "app_theme": app_theme,
                    "app_env": app_env,
                }
            except Exception as e:
                logger.error("Failed to retrieve custom server configs.")
                raise CustomConfigsNotFoundException(e)

        if config_type == ServerConfigType.JSON:
            return json.dumps(self.configs, indent=4, ensure_ascii=False).encode(Encoding.UTF8).decode()
        else:
            return self.configs
