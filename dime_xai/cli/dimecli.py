import logging
from typing import Dict, NoReturn, Text

from dime_xai.core.custom_dime_explainer import CustomDIMEExplainer
from dime_xai.core.dime_core import load_explanation
from dime_xai.core.rasa_dime_explainer import RasaDIMEExplainer
from dime_xai.shared.constants import (
    MODEL_TYPE_DIET,
    MODEL_TYPE_OTHER,
    DIMEConfig,
    MODEL_MODE_REST,
    OUTPUT_MODE_GLOBAL,
)
from dime_xai.shared.exceptions.dime_base_exception import DIMEBaseException
from dime_xai.shared.exceptions.dime_core_exceptions import (
    InvalidDIMEExplanationFilePath,
    DIMEExplanationFileLoadException,
    DIMEExplanationDirectoryException,
    DIMEExplanationFileExistsException,
    InvalidDIMEExplanationStructure,
    RESTModelLoadException,
)
from dime_xai.shared.exceptions.dime_io_exceptions import EmptyNLUDatasetException
from dime_xai.utils.io import exit_dime

logger = logging.getLogger(__name__)


class DimeCLIExplainer:
    def __init__(
            self,
            configs: Dict = None,
    ) -> NoReturn:
        self.configs = configs

    def run(self):
        logger.debug("Initializing DIME CLI Explainer...")
        model_type = self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_MODEL_TYPE]
        model_mode = self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_MODEL_MODE]
        output_mode = self.configs[DIMEConfig.MAIN_KEY_CLI][DIMEConfig.SUB_KEY_CLI_OUTPUT_MODE]

        # Deprecations, Errors and Warnings
        # in DIME configs and CLI arguments
        if model_mode == MODEL_MODE_REST:
            logger.warning("Support for REST models is still experimental and "
                           "could be removed in the upcoming DIME versions "
                           "due to performance issues.")

            if output_mode == OUTPUT_MODE_GLOBAL:
                logger.error(f"Global feature importance cannot be calculated on REST "
                             f"models. Please try loading a local model instead.")
                exit_dime(1)

        try:
            if model_type == MODEL_TYPE_DIET:
                rasa_dime_explainer = RasaDIMEExplainer(
                    models_path=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_MODELS_PATH],
                    model_name=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_MODEL_NAME],
                    testing_data_path=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_DATA_PATH],
                    model_mode=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_MODEL_MODE],
                    rasa_version=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_RASA_VERSION],
                    url=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_URL_ENDPOINT],
                    data_instances=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_DATA_INSTANCE],
                    ranking_length=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_RANKING_LENGTH],
                    ngrams=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_NGRAMS],
                    min_ngrams=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_NGRAMS_MIN],
                    max_ngrams=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_NGRAMS_MAX],
                    case_sensitive=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_CASE_SENSITIVITY],
                    global_metric=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_GLOBAL_METRIC],
                    output_mode=self.configs[DIMEConfig.MAIN_KEY_CLI][DIMEConfig.SUB_KEY_CLI_OUTPUT_MODE],
                )
                explanation = rasa_dime_explainer.explain()
                explanation.visualize()
            elif model_type == MODEL_TYPE_OTHER:
                custom_dime_explainer = CustomDIMEExplainer(
                    models_path=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_MODELS_PATH],
                    model_name=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_MODEL_NAME],
                    testing_data_path=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_DATA_PATH],
                    model_mode=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_MODEL_MODE],
                    url=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_URL_ENDPOINT],
                    data_instances=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_DATA_INSTANCE],
                    ranking_length=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_RANKING_LENGTH],
                    ngrams=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_NGRAMS],
                    min_ngrams=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_NGRAMS_MIN],
                    max_ngrams=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_NGRAMS_MAX],
                    case_sensitive=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_CASE_SENSITIVITY],
                    global_metric=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_GLOBAL_METRIC],
                    output_mode=self.configs[DIMEConfig.MAIN_KEY_CLI][DIMEConfig.SUB_KEY_CLI_OUTPUT_MODE],
                )
                explanation = custom_dime_explainer.explain()
                explanation.visualize()
        except EmptyNLUDatasetException as e:
            logger.error(f"Got an empty dataset. Possibly a YAML format issue. {e}")
        except InvalidDIMEExplanationFilePath as e:
            logger.error(e)
        except DIMEExplanationFileLoadException as e:
            logger.error(e)
        except DIMEExplanationDirectoryException as e:
            logger.error(e)
        except DIMEExplanationFileExistsException as e:
            logger.error(e)
        except InvalidDIMEExplanationStructure as e:
            logger.error(e)
        except RESTModelLoadException as e:
            logger.error(e)
        except DIMEBaseException as e:
            logger.error(f"Unknown Base Exception {e}")
        except KeyboardInterrupt:
            logger.info(f"Gracefully terminating DIME CLI Explainer...")
            exit_dime(1)
        except MemoryError as e:
            logger.info(f"Out of memory exception occurred while loading the model. {e}")
            exit_dime(1)
        except OSError as e:
            logger.info(f"OSError exception occurred while loading the model. {e}")
            exit_dime(1)
        except Exception as e:
            logger.error(f"Unknown CLI Exception {e}")


class DimeCLIVisualizer:
    def __init__(
            self,
            file_name: Text = None,
            limit: int = None,
    ) -> NoReturn:
        self.file_name = file_name
        self.limit = limit

    def run(self):
        logger.debug("Initializing DIME CLI Visualizer...")

        try:
            explanation = load_explanation(explanation=self.file_name)
            explanation.visualize(token_limit=self.limit)

        except InvalidDIMEExplanationFilePath as e:
            logger.error(e)
        except DIMEExplanationFileLoadException as e:
            logger.error(e)
        except DIMEExplanationDirectoryException as e:
            logger.error(e)
        except InvalidDIMEExplanationStructure as e:
            logger.error(e)
        except DIMEBaseException as e:
            logger.error(f"Unknown Base Exception {e}")
        except KeyboardInterrupt:
            logger.info(f"Gracefully terminating DIME CLI Visualizer...")
            exit_dime(1)
        except Exception as e:
            logger.error(f"Unknown CLI Exception {e}")
