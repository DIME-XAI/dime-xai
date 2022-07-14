import logging
import sys
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
    ExplanationType,
)
from dime_xai.shared.exceptions.dime_base_exception import DIMEBaseException
from dime_xai.shared.exceptions.dime_core_exceptions import (
    InvalidDIMEExplanationFilePath,
    DIMEExplanationFileLoadException,
    DIMEExplanationDirectoryException,
    DIMEExplanationFileExistsException,
    InvalidDIMEExplanationStructure,
    RESTModelLoadException,
    ModelFingerprintPersistException,
    DataFingerprintPersistException,
    DIMEFingerprintPersistException,
    InvalidMetricSpecifiedException,
    InvalidIntentRankingException,
    NLUDataTaggingException,
    EmptyIntentRankingException,
    DIMECoreException,
    DatasetParseException,
    RasaModelLoadException,
    RasaExplainerException,
)
from dime_xai.shared.exceptions.dime_io_exceptions import (
    EmptyNLUDatasetException,
    InvalidFileExtensionException,
)
from dime_xai.utils import process
from dime_xai.utils.io import exit_dime

logger = logging.getLogger(__name__)


class DimeCLIExplainer:
    """
    Initializes DIME CLI Explainer interface.
    Calls the relevant explainer classes based
    on the model type provided in the
    dime_config.yml configurations.
    """
    def __init__(
            self,
            configs: Dict = None,
            quiet_mode: bool = False,
            request_id: Text = None,
    ) -> NoReturn:
        self.configs = configs
        self.quiet_mode = quiet_mode
        self.request_id = request_id

    def run(self) -> NoReturn:
        """
        Runs the DIME CLI Explainer. Can recognize the model type
        and call relevant DIME core explainers and pass required
        configurations

        Returns:
            no return
        """
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
                             f"models while using DIME CLI/SERVER. Please try loading "
                             f"a local model instead. Try jupyter notebooks using DIME "
                             f"API to get global feature importance from a REST model")
                exit_dime("output model error")

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
                    metric=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_METRIC],
                    output_mode=self.configs[DIMEConfig.MAIN_KEY_CLI][DIMEConfig.SUB_KEY_CLI_OUTPUT_MODE],
                    quiet_mode=self.quiet_mode,
                )
                if self.quiet_mode:
                    explanation = rasa_dime_explainer.explain(inspect=False)
                    metadata = explanation.get_explanation(output_type=ExplanationType.QUIET)
                    process_q = process.ProcessQueue()
                    process_q.update_metadata(
                        request_id=self.request_id,
                        metadata=metadata
                    )
                    sys.stdout.write(f"success {self.request_id}")
                else:
                    explanation = rasa_dime_explainer.explain(inspect=True)
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
                    metric=self.configs[DIMEConfig.MAIN_KEY_BASE][DIMEConfig.SUB_KEY_BASE_METRIC],
                    output_mode=self.configs[DIMEConfig.MAIN_KEY_CLI][DIMEConfig.SUB_KEY_CLI_OUTPUT_MODE],
                    quiet_mode=self.quiet_mode,
                )
                explanation = custom_dime_explainer.explain()
                if self.quiet_mode:
                    sys.stdout.write(explanation.get_explanation(output_type=ExplanationType.QUIET))
                else:
                    explanation.visualize()

        # Training data exceptions
        except EmptyNLUDatasetException as e:
            logger.error(e)
            exit_dime("empty nlu data error") if self.quiet_mode else exit_dime()
        except InvalidFileExtensionException as e:
            logger.error(e)
            exit_dime("file ext error") if self.quiet_mode else exit_dime()
        except NLUDataTaggingException as e:
            logger.error(e)
            exit_dime("nlu data tagging error") if self.quiet_mode else exit_dime()
        # Dataset parsing exceptions
        except RasaModelLoadException as e:
            logger.error(e)
            exit_dime("rasa model error") if self.quiet_mode else exit_dime()
        except DatasetParseException as e:
            logger.error(e)
            exit_dime("data parse error") if self.quiet_mode else exit_dime()
        # Fingerprinting exceptions
        except ModelFingerprintPersistException as e:
            logger.error(e)
            exit_dime("model fp error") if self.quiet_mode else exit_dime()
        except DataFingerprintPersistException as e:
            logger.error(e)
            exit_dime("data fp error") if self.quiet_mode else exit_dime()
        except DIMEFingerprintPersistException as e:
            logger.error(e)
            exit_dime("fp save error") if self.quiet_mode else exit_dime()
        # DIME Core exceptions
        except EmptyIntentRankingException as e:
            logger.error(e)
            exit_dime("intent rank error") if self.quiet_mode else exit_dime()
        except InvalidMetricSpecifiedException as e:
            logger.error(e)
            exit_dime("metric error") if self.quiet_mode else exit_dime()
        except InvalidIntentRankingException as e:
            logger.error(e)
            exit_dime("ranking length error") if self.quiet_mode else exit_dime()
        # DIME Explanation exceptions
        except InvalidDIMEExplanationFilePath as e:
            logger.error(e)
            exit_dime("exp path error") if self.quiet_mode else exit_dime()
        except DIMEExplanationFileLoadException as e:
            logger.error(e)
            exit_dime("exp load error") if self.quiet_mode else exit_dime()
        except DIMEExplanationDirectoryException as e:
            logger.error(e)
            exit_dime("exp dir error") if self.quiet_mode else exit_dime()
        except DIMEExplanationFileExistsException as e:
            logger.error(e)
            exit_dime("exp ext error") if self.quiet_mode else exit_dime()
        except InvalidDIMEExplanationStructure as e:
            logger.error(e)
            exit_dime("exp structure error") if self.quiet_mode else exit_dime()
        # Model exceptions
        except RESTModelLoadException as e:
            logger.error(e)
            exit_dime("rest model error") if self.quiet_mode else exit_dime()
        # DIME Base exceptions
        except RasaExplainerException as e:
            logger.error(e)
            exit_dime("rasa explainer error") if self.quiet_mode else exit_dime()
        except DIMECoreException as e:
            logger.error(f"Unknown Core Exception {e}")
            exit_dime("core error") if self.quiet_mode else exit_dime()
        except DIMEBaseException as e:
            logger.error(f"Unknown Base Exception {e}")
            exit_dime("base error") if self.quiet_mode else exit_dime()
        # Default exceptions
        except KeyboardInterrupt:
            logger.info(f"Gracefully terminating DIME CLI Explainer...")
            exit_dime("keyboard error") if self.quiet_mode else exit_dime()
        except MemoryError as e:
            logger.info(f"Out of memory exception occurred while loading the model. {e}")
            exit_dime("memory error") if self.quiet_mode else exit_dime()
        except OSError as e:
            logger.info(f"OSError exception occurred while loading the model. {e}")
            exit_dime("os error") if self.quiet_mode else exit_dime()
        except Exception as e:
            logger.error(f"Unknown CLI Exception. {e}")
            exit_dime("generic error") if self.quiet_mode else exit_dime()


class DimeCLIVisualizer:
    """
    Initializes DIME CLI Visualizer interface.
    Allows loading external explanations and
    visualize them in the CLI
    """

    def __init__(
            self,
            file_name: Text = None,
            limit: int = None,
    ) -> NoReturn:
        self.file_name = file_name
        self.limit = limit

    def run(self) -> NoReturn:
        """
        Runs the DIME CLI Visualizer. Passes the explanation
        file name as an argument to the DIMEExplanation class
        and invokes visualize method on the explanation object

        Returns:
            no return
        """
        logger.debug("Initializing DIME CLI Visualizer...")

        try:
            explanation = load_explanation(explanation=self.file_name)
            explanation.visualize(token_limit=self.limit)
        # DIME explanation exceptions
        except InvalidDIMEExplanationFilePath as e:
            logger.error(e)
            exit_dime()
        except DIMEExplanationFileLoadException as e:
            logger.error(e)
            exit_dime()
        except DIMEExplanationDirectoryException as e:
            logger.error(e)
            exit_dime()
        except InvalidDIMEExplanationStructure as e:
            logger.error(e)
            exit_dime()
        # DIME Base exceptions
        except DIMECoreException as e:
            logger.error(f"Unknown Core Exception {e}")
            exit_dime()
        except DIMEBaseException as e:
            logger.error(f"Unknown Base Exception {e}")
            exit_dime()
        # Default exceptions
        except KeyboardInterrupt:
            logger.info(f"Gracefully terminating DIME CLI Visualizer...")
            exit_dime()
        except Exception as e:
            logger.error(f"Unknown CLI Exception {e}")
            exit_dime()
