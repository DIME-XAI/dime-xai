import os.path
from typing import Optional, Text

PACKAGE_NAME = "dime"
PACKAGE_NAME_PIPY = "dime_xai"
PACKAGE_VERSION = "0.0.3a5"
PACKAGE_VERSION_LONG = f'DIME Version:{PACKAGE_VERSION}\n[Supported RASA Version:\t2.x.x]'
RASA_CORE_VERSION = "2.8.8"
RASA_SDK_VERSION = "2.8.4"
LANGUAGES_SUPPORTED = ['en', 'si']

DEFAULT_DATA_PATH = "./data"
FILE_READ_PERMISSION = "r"
FILE_ENCODING_UTF8 = "utf8"
YAML_EXTENSIONS = [".yml", ".yaml"]
INVALID_DIR_NAME_CHARS = ['\\', '/', '<', '>', ':', '*', '?', '|']
ALLOWED_INIT_DIR_NAMES = [".", "./", "None", "none"]

DEFAULT_NLU_YAML_VERSION = "2.0"
DEFAULT_NLU_YAML_TAG = "nlu"
DEFAULT_VERSION_YAML_TAG = "version"
DEFAULT_NLU_INTENT_TAG = "intent"
DEFAULT_NLU_EXAMPLES_TAG = "examples"
DEFAULT_LATEST_TAG = "latest"
RASA_MODEL_EXTENSIONS = [".tar.gz"]
RASA_288_MODEL_REGEX = r"^(\d{8})\-(\d{6}).tar.gz$"

DEFAULT_CACHE_PATH = "./.dime_cache"

# fingerprinting
DEFAULT_FINGERPRINT_FILE = "dime_fingerprint.json"
DEFAULT_MODEL_FINGERPRINT_FILE = "dime_model_fingerprint.json"
DEFAULT_DATA_FINGERPRINT_FILE = "dime_data_fingerprint.json"
DEFAULT_FINGERPRINT_PERSIST_PATH = os.path.join(DEFAULT_CACHE_PATH, DEFAULT_FINGERPRINT_FILE)
DEFAULT_MODEL_FINGERPRINT_PERSIST_PATH = os.path.join(DEFAULT_CACHE_PATH, DEFAULT_MODEL_FINGERPRINT_FILE)
DEFAULT_DATA_FINGERPRINT_PERSIST_PATH = os.path.join(DEFAULT_CACHE_PATH, DEFAULT_DATA_FINGERPRINT_FILE)

# result persisting
DEFAULT_PERSIST_PATH = "./dime_explanations"
DEFAULT_PERSIST_FILE = "dime_results"
DEFAULT_PERSIST_EXTENSION = ".json"


DEFAULT_MODELS_PATH = "./models"
MODEL_TYPE_DIET = "diet"
MODEL_TYPE_OTHER = "other"
NLU_FALLBACK_TAG = "nlu_fallback"
DEFAULT_MODEL_TYPE = MODEL_TYPE_DIET
ALLOWED_RASA_VERSIONS = ['2.0.0', '2.0.1', '2.0.2', '2.0.3', '2.0.4',
                         '2.0.5', '2.0.6', '2.0.7', '2.0.8', '2.1.0',
                         '2.1.1', '2.1.2', '2.1.3', '2.2.0a1', '2.2.0',
                         '2.2.1', '2.2.2', '2.2.3', '2.2.4', '2.2.5',
                         '2.2.6', '2.2.7', '2.2.8', '2.2.9', '2.2.10',
                         '2.3.0', '2.3.1', '2.3.2', '2.3.3', '2.3.4',
                         '2.3.5', '2.4.0', '2.4.1', '2.4.2', '2.4.3',
                         '2.5.0', '2.5.1', '2.5.2', '2.6.0', '2.6.1',
                         '2.6.2', '2.6.3', '2.7.0', '2.7.1', '2.7.2',
                         '2.8.0', '2.8.1', '2.8.2', '2.8.3', '2.8.4',
                         '2.8.5', '2.8.6', '2.8.7', '2.8.8', '2.8.9',
                         '2.8.10', '2.8.11', '2.8.12', '2.8.13', '2.8.14',
                         '2.8.15', '2.8.16', '2.8.17', '2.8.18', '2.8.19',
                         '2.8.20', '2.8.21', '2.8.22', '2.8.23', '2.8.24',
                         '2.8.25', '2.8.26', '2.8.27']
MODEL_MODE_REST = "rest"
MODEL_MODE_LOCAL = "local"
DEFAULT_MODEL_MODE = MODEL_MODE_REST
RASA_REST_WEBHOOK = "/webhooks/rest/webhook"
RASA_CORE_URL = "http://localhost:5005"
MODEL_REST_WEBHOOK_URL = "http://localhost:5005/webhooks/rest/webhook"
RASA_REST_ENDPOINT_PARSE = "/model/parse"
OUTPUT_MODE_DUAL = "dual"
OUTPUT_MODE_GLOBAL = "global"
DEFAULT_OUTPUT_MODE = OUTPUT_MODE_DUAL
DEFAULT_RANKING_LENGTH = 10
DEFAULT_NGRAMS_MODE = False
DEFAULT_MIN_NGRAMS = 0
DEFAULT_MAX_NGRAMS = 4
DEFAULT_CASE_SENSITIVE_MODE = True
DEFAULT_DATAFRAME_MODE = False

DEFAULT_DIME_SERVER_PORT = 6066
DEFAULT_DIME_SERVER_LOCALHOST_DEC = "0.0.0.0"
DEFAULT_DIME_SERVER_LOCALHOST = "localhost"

DEFAULT_EXAMPLE_INSTANCE = "SLIIT විසින් පිරිනමනු ලබන IT උපාධි මොනවාද?"
RANKING_LENGTH = 10

# scaffold
DEFAULT_INIT_SRC_DIR_NAME = "init_dir"
DEFAULT_INIT_CACHE_DIR_NAME = ".dime_init_"
DEFAULT_INIT_FILES_TO_EXCLUDE = ['__init__.py', '__pycache__', '__main__.py']
DEFAULT_INIT_DEST_DIR_NAME = "./"
RASA_DIRS_IN_DIME_INIT = ["data", "models"]

# dime explanations
DEFAULT_DIME_EXPLANATION_BASE_KEYS = ['global', 'dual', 'config', 'timestamp', 'data', 'model']
DEFAULT_DIME_EXPLANATION_TIMESTAMP_KEYS = ['start', 'end']
DEFAULT_DIME_EXPLANATION_MODEL_KEYS = ['fingerprint', 'name', 'version', 'type', 'path', 'mode', 'url']
DEFAULT_DIME_EXPLANATION_DATA_KEYS = ['fingerprint', 'tokens', 'vocabulary', 'instances', 'intents', 'path']
DEFAULT_DIME_EXPLANATION_CONFIG_KEYS = ['case_sensitive', 'output_mode', 'ranking_length', 'metric', 'ngrams']
DEFAULT_DIME_EXPLANATION_NGRAMS_KEYS = ['min_ngrams', 'max_ngrams']
DEFAULT_DIME_EXPLANATION_GLOBAL_KEYS = ['feature_importance', 'normalized_scores', 'probability_scores']
DEFAULT_DIME_EXPLANATION_DUAL_KEYS = ['instance', 'global', 'dual']
DEFAULT_DIME_EXPLANATION_DUAL_SUB_GLOBAL = ['feature_importance', 'feature_selection', 'normalized_scores',
                                            'probability_scores', 'predicted_intent', 'predicted_confidence']
DEFAULT_DIME_EXPLANATION_DUAL_SUB_DUAL = ['feature_importance', 'normalized_scores', 'probability_scores',
                                          'test_norm_glob_prob', 'test_norm_dual_prob']
DEFAULT_VISUALIZATIONS_LIMIT = 10


class InterfaceType:
    INTERFACE_INIT = "init"
    INTERFACE_CLI = "cli"
    INTERFACE_CLI_EXPLAINER = "explain"
    INTERFACE_CLI_VISUALIZER = "visualize"
    INTERFACE_SERVER = "server"
    INTERFACE_NONE = ""


class TermColor:
    # source:
    # https://pkg.go.dev/github.com/whitedevops/colors

    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END_C = "\033[0m"
    NONE_C = ""

    DEFAULT = "\033[39m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    LIGHTGRAY = "\033[37m"
    DARKGRAY = "\033[90m"
    LIGHTRED = "\033[91m"
    LIGHTGREEN = "\033[92m"
    LIGHTYELLOW = "\033[93m"
    LIGHTBLUE = "\033[94m"
    LIGHTMAGENTA = "\033[95m"
    LIGHTCYAN = "\033[96m"
    WHITE = "\033[97m"

    BDEFAULT = "\033[49m"
    BBLACK = "\033[40m"
    BRED = "\033[41m"
    BGREEN = "\033[42m"
    BYELLOW = "\033[43m"
    BBLUE = "\033[44m"
    BMAGENTA = "\033[45m"
    BCYAN = "\033[46m"
    BGRAY = "\033[47m"
    BDARKGRAY = "\033[100m"
    BLIGHTRED = "\033[101m"
    BLIGHTGREEN = "\033[102m"
    BLIGHTYELLOW = "\033[103m"
    BLIGHTBLUE = "\033[104m"
    BLIGHTMAGENTA = "\033[105m"
    BLIGHTCYAN = "\033[106m"
    BWHITE = "\033[107m"


class CLIOutput:
    GLOBAL = "global"
    LOCAL = "local"
    ALL = "all"
    RAW_GLOBAL = "raw_global"
    RAW_LOCAL = "raw_local"
    RAW_ALL = "raw"


class DestinationDirType:
    RASA = "rasa"
    DIME = "dime"
    EMPTY = "empty"
    VALID = "valid"
    INVALID = "invalid"


DEFAULT_CONFIG_FILE_PATH = "./dime_config.yml"


class DIMEConfig:
    MAIN_KEY_BASE = 'dime_base_configs'
    MAIN_KEY_SERVER = 'dime_server_configs'
    MAIN_KEY_CLI = 'dime_cli_configs'

    MAIN_CONFIG_KEYS = {'dime_base_configs': ['languages', 'data_path', 'models_path', 'model_type', 'model_mode',
                                              'url_endpoint', 'data_instance', 'ranking_length',
                                              'ngrams', 'case_sensitive', 'metric'],
                        'dime_server_configs': ['host', 'port', 'output_mode'],
                        'dime_cli_configs': ['output_mode']}

    ALL_KEYS = ['dime_base_configs', 'data_path', 'models_path', 'model_type', 'model_mode',
                'url_endpoint', 'data_instance', 'ranking_length', 'ngrams', 'case_sensitive',
                'metric', 'dime_server_configs', 'host', 'port', 'dime_cli_configs', 'output_mode']

    BASE_CONFIG_PROPS = {'ngrams': ['max_ngrams', 'min_ngrams'],
                         'models_path': ['model_name'],
                         'model_type': ['rasa_version']}

    SERVER_CONFIG_PROPS = {}
    CLI_CONFIG_PROPS = {}

    SUB_KEY_BASE_LANGUAGES = "languages"
    SUB_KEY_BASE_DATA_PATH = "data_path"
    SUB_KEY_BASE_MODELS_PATH = "models_path"
    SUB_KEY_BASE_MODEL_NAME = "model_name"
    SUB_KEY_BASE_MODEL_TYPE = "model_type"
    SUB_KEY_BASE_RASA_VERSION = "rasa_version"
    SUB_KEY_BASE_MODEL_MODE = "model_mode"
    SUB_KEY_BASE_URL_ENDPOINT = "url_endpoint"
    SUB_KEY_BASE_DATA_INSTANCE = "data_instance"
    SUB_KEY_BASE_RANKING_LENGTH = "ranking_length"
    SUB_KEY_BASE_NGRAMS = "ngrams"
    SUB_KEY_BASE_NGRAMS_MAX = "max_ngrams"
    SUB_KEY_BASE_NGRAMS_MIN = "min_ngrams"
    SUB_KEY_BASE_CASE_SENSITIVITY = "case_sensitive"
    SUB_KEY_BASE_METRIC = "metric"
    SUB_KEY_SERVER_HOST = 'host'
    SUB_KEY_SERVER_PORT = 'port'
    SUB_KEY_CLI_OUTPUT_MODE = 'output_mode'
    SUB_KEY_CLI_EXPLANATION_FILE = 'explanation_file'

    @staticmethod
    def verify_config_key(key_name: Text) -> Optional[bool]:
        return key_name in DIMEConfig.ALL_KEYS

    @staticmethod
    def verify_base_config_key(key_name: Text) -> Optional[bool]:
        return key_name in DIMEConfig.MAIN_CONFIG_KEYS[DIMEConfig.MAIN_KEY_BASE]

    @staticmethod
    def verify_server_config_key(key_name: Text) -> Optional[bool]:
        return key_name in DIMEConfig.MAIN_CONFIG_KEYS[DIMEConfig.MAIN_KEY_SERVER]

    @staticmethod
    def verify_cli_config_key(key_name: Text) -> Optional[bool]:
        return key_name in DIMEConfig.MAIN_CONFIG_KEYS[DIMEConfig.MAIN_KEY_CLI]

    @staticmethod
    def get_main_keys_length() -> Optional[int]:
        return len(DIMEConfig.MAIN_CONFIG_KEYS)

    @staticmethod
    def get_base_keys_length() -> Optional[int]:
        return len(DIMEConfig.MAIN_CONFIG_KEYS[DIMEConfig.MAIN_KEY_BASE])

    @staticmethod
    def get_server_keys_length() -> Optional[int]:
        return len(DIMEConfig.MAIN_CONFIG_KEYS[DIMEConfig.MAIN_KEY_SERVER])

    @staticmethod
    def get_cli_keys_length() -> Optional[int]:
        return len(DIMEConfig.MAIN_CONFIG_KEYS[DIMEConfig.MAIN_KEY_CLI])


class Metrics:
    F1_SCORE = 'f1-score'
    ACCURACY = 'accuracy'
    CONFIDENCE = 'confidence'
    DEFAULT = F1_SCORE

    # F1 Score Configs
    AVG_MICRO = 'micro'
    AVG_MACRO = 'macro'
    AVG_WEIGHTED = 'weighted'
    AVG_NONE = None

    # Accuracy Configs
    NORMALIZE = True

    # Confidence Configs
    TOTAL_CONFIDENCE = 'sum'


class Smoothing:
    LAPLACE = 'laplace'
