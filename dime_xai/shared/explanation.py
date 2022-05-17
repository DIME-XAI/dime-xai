import json
import logging
import os
from typing import Dict, Union, Text, Optional, NoReturn, List

from termgraph import termgraph as tg

from dime_xai.shared.constants import (
    DEFAULT_PERSIST_PATH,
    DEFAULT_PERSIST_FILE,
    DEFAULT_PERSIST_EXTENSION,
    DEFAULT_DIME_EXPLANATION_BASE_KEYS,
    DEFAULT_DIME_EXPLANATION_DATA_KEYS,
    DEFAULT_DIME_EXPLANATION_MODEL_KEYS,
    DEFAULT_DIME_EXPLANATION_TIMESTAMP_KEYS,
    DEFAULT_DIME_EXPLANATION_CONFIG_KEYS,
    DEFAULT_DIME_EXPLANATION_NGRAMS_KEYS,
    OUTPUT_MODE_GLOBAL,
    OUTPUT_MODE_DUAL,
    DEFAULT_DIME_EXPLANATION_GLOBAL_KEYS,
    DEFAULT_DIME_EXPLANATION_DUAL_SUB_GLOBAL,
    DEFAULT_DIME_EXPLANATION_DUAL_SUB_DUAL,
    DEFAULT_DIME_EXPLANATION_DUAL_KEYS,
)
from dime_xai.shared.exceptions.dime_core_exceptions import (
    InvalidDIMEExplanationFilePath,
    DIMEExplanationFileLoadException,
    DIMEExplanationDirectoryException,
    DIMEExplanationFileExistsException,
    DIMEExplanationFilePersistException,
    InvalidDIMEExplanationStructure,
)
from dime_xai.utils.io import (
    file_exists,
    get_timestamp_str,
    dir_exists,
)

logger = logging.getLogger(__name__)


class DIMEExplanation:
    def __init__(self, explanation: Union[Dict, Text]):
        if isinstance(explanation, Text):
            full_file_path = os.path.join(DEFAULT_PERSIST_PATH, explanation)
            if not file_exists(full_file_path):
                raise InvalidDIMEExplanationFilePath(f"The provided explanation file name is invalid. "
                                                     f"Make sure that it is available in the "
                                                     f"dime_explanations directory")

            self.file_name = explanation

            try:
                with open(full_file_path, encoding='utf8', mode='r') as file:
                    self.explanation = json.load(file)
            except Exception as e:
                raise DIMEExplanationFileLoadException(f"Error occurred while reading "
                                                       f"the explanation file specified. {e}")
        else:
            self.file_name = DEFAULT_PERSIST_FILE + "_" + \
                             get_timestamp_str(sep="_") + \
                             DEFAULT_PERSIST_EXTENSION
            self.explanation = explanation

        if not self._validate():
            raise InvalidDIMEExplanationStructure(f"The structure of the provided DIME "
                                                  f"explanation file is invalid.")

    def persist(
            self,
            name: Text = None,
            overwrite: bool = False
    ) -> Optional[Text]:
        if not dir_exists(DEFAULT_PERSIST_PATH):
            logger.warning("The default explanation directory does not exist. "
                           "A new directory will be created to persist the "
                           "DIME explanations.")
            try:
                os.mkdir(DEFAULT_PERSIST_PATH)
            except OSError:
                raise DIMEExplanationDirectoryException(f"Error occurred while attempting "
                                                        f"to create the explanations "
                                                        f"directory")

        if not name:
            name = self.file_name

        full_file_path = os.path.join(
            DEFAULT_PERSIST_PATH,
            name
        )

        if file_exists(full_file_path):
            if overwrite:
                logger.warning("A file with the same name is available in the specified "
                               "location and will be overwritten.")
            else:
                raise DIMEExplanationFileExistsException("A file with the same name is "
                                                         "available in the specified "
                                                         "location. Explanations will not "
                                                         "be persisted.")

        try:
            with open(full_file_path, encoding='utf8', mode='w') as file:
                json.dump(self.explanation, file, indent=4, ensure_ascii=False)

            logger.info(f"DIME explanations were persisted in dime_explanations directory under "
                        f"{self.file_name}")
            return self.file_name

        except Exception as e:
            raise DIMEExplanationFilePersistException(f"Failed to persist "
                                                      f"DIME explanations in "
                                                      f"the given destination: "
                                                      f"{full_file_path}. {e}")

    def _validate(self) -> bool:
        for key in list(self.explanation.keys()):
            if key not in DEFAULT_DIME_EXPLANATION_BASE_KEYS:
                logger.error(f"Invalid key '{key}' found under DIME explanation's main keys")
                return False

        for key in list(self.explanation['data'].keys()):
            if key not in DEFAULT_DIME_EXPLANATION_DATA_KEYS:
                logger.error(f"Invalid key '{key}' found under DIME explanation's 'data' key")
                return False

        for key in list(self.explanation['model'].keys()):
            if key not in DEFAULT_DIME_EXPLANATION_MODEL_KEYS:
                logger.error(f"Invalid key '{key}' found under DIME explanation's 'model' key")
                return False

        for key in list(self.explanation['timestamp'].keys()):
            if key not in DEFAULT_DIME_EXPLANATION_TIMESTAMP_KEYS:
                logger.error(f"Invalid key '{key}' found under DIME explanation's 'timestamp' key")
                return False

        for key in list(self.explanation['config'].keys()):
            if key not in DEFAULT_DIME_EXPLANATION_CONFIG_KEYS:
                logger.error(f"Invalid key '{key}' found under DIME explanation's 'config' key")
                return False

        if isinstance(self.explanation['config']['ngrams'], Dict):
            for key in list(self.explanation['ngrams'].keys()):
                if key not in DEFAULT_DIME_EXPLANATION_NGRAMS_KEYS:
                    logger.error(f"Invalid key '{key}' found under DIME explanation's 'ngrams' key")
                    return False

        if self.explanation['config']['output_mode'] == OUTPUT_MODE_GLOBAL:
            for key in self.explanation['global']:
                if key not in DEFAULT_DIME_EXPLANATION_GLOBAL_KEYS:
                    logger.error(f"Invalid key '{key}' found under DIME explanation's 'output_mode' key")
                    return False

        if self.explanation['config']['output_mode'] == OUTPUT_MODE_DUAL:
            for instance in self.explanation['dual']:
                for key in instance:
                    if key not in DEFAULT_DIME_EXPLANATION_DUAL_KEYS:
                        logger.error(f"Invalid key '{key}' found under DIME explanation's 'dual' key")
                        return False
                    if key == 'global':
                        for subkey in instance[key]:
                            if subkey not in DEFAULT_DIME_EXPLANATION_DUAL_SUB_GLOBAL:
                                logger.error(f"Invalid key '{subkey}' found under DIME "
                                             f"explanation's 'dual > global' key")
                                return False
                    if key == 'dual':
                        for subkey in instance[key]:
                            if subkey not in DEFAULT_DIME_EXPLANATION_DUAL_SUB_DUAL:
                                logger.error(f"Invalid key '{subkey}' found under DIME "
                                             f"explanation's 'dual > dual' key")
                                return False

        return True

    def inspect(self) -> NoReturn:
        exp_json = json.dumps(self.explanation, indent=4, ensure_ascii=False).encode('utf8')
        print(f"\nDIME Explanations [Raw]: \n\n{exp_json.decode()}\n")

    @staticmethod
    def _visualize_cli_chart(
            title: Text,
            description: Text,
            labels: List,
            data: List[List],
            width: int = 50,
            color: int = 97,
    ) -> NoReturn:
        print(f"\n{title}\n") if title else None
        print(f"{description}\n") if description else None
        normal_data = tg.normalize(data, width=width)
        len_cats = 1
        args = {'filename': '', 'title': '', 'width': width,
                'format': '{:<}', 'suffix': '', 'no_labels': False,
                'color': None, 'vertical': True, 'stacked': False,
                'different_scale': False, 'calendar': False,
                'start_dt': None, 'custom_tick': '', 'delim': '',
                'verbose': False, 'version': False}
        colors = [color]
        tg.stacked_graph(labels=labels, data=data, normal_data=normal_data,
                         len_categories=len_cats, colors=colors, args=args)

    def _visualize_global(
            self,
            title: Text,
            main_description: Text,
            instance: Dict,
            global_only: bool = False,
            token_limit: int = None,
    ) -> NoReturn:
        if global_only:
            if token_limit is None:
                logger.warning(f"The token limit has not been specified and was "
                               f"set to 10. To visualize global feature importance of "
                               f"all tokens, specify '--limit' as 0")
                token_limit = 10
            elif token_limit == 0:
                logger.warning(f"Token limit will be ignored and all tokens "
                               f"will be visualized")

            max_token_limit = len(self.explanation['global']['normalized_scores'].keys())
            if token_limit > max_token_limit or token_limit == 0:
                token_limit = max_token_limit

            global_title = f"GLOBAL FEATURE IMPORTANCE SCORES"
            global_description = f"{main_description}"
            global_proba_labels = list(self.explanation['global']['probability_scores'].keys())[0:token_limit]
            global_proba_data = [[score] for score
                                 in list(self.explanation['global']['probability_scores'].values())[0:token_limit]]
        else:
            global_title = f"{title} FEATURE IMPORTANCE SCORES\nDATA INSTANCE: {instance['instance']}"
            global_title += f"\nPREDICTED INTENT: {instance['global']['predicted_intent']}"
            global_title += f"\nCONFIDENCE: {instance['global']['predicted_confidence']}"
            gfi = [f'{t}={s}' for t, s in instance['global']['feature_importance'].items()]
            gfs = [f'{t}' for t in instance['global']['feature_selection'].keys()]
            gfw = [f'{t}={s}' for t, s in instance['global']['normalized_scores'].items()]
            gfp = [f'{t}={s}' for t, s in instance['global']['probability_scores'].items()]
            global_description = f"{main_description}" \
                                 f"Ranking Length: {self.explanation['config']['ranking_length']}\n\n" \
                                 f"Global feature importance scores (Raw): \t" \
                                 f"{', '.join(gfi)}\n" \
                                 f"Selected token list based on global score: \t" \
                                 f"{', '.join(gfs)}\n" \
                                 f"Global feature importance scores (Normalized): \t" \
                                 f"{', '.join(gfw)}\n" \
                                 f"Global feature importance probability scores: \t" \
                                 f"{', '.join(gfp)}\n"

            global_proba_labels = list(instance['global']['probability_scores'].keys())
            global_proba_data = [[score] for score
                                 in list(instance['global']['probability_scores'].values())]

        DIMEExplanation._visualize_cli_chart(
            title=global_title,
            description=global_description,
            labels=global_proba_labels,
            data=global_proba_data,
        )

    @staticmethod
    def _visualize_dual(instance: Dict) -> NoReturn:
        dfi = [f'{t}={s}' for t, s in instance['dual']['feature_importance'].items()]
        dfw = [f'{t}={s}' for t, s in instance['dual']['normalized_scores'].items()]
        dfp = [f'{t}={s}' for t, s in instance['dual']['probability_scores'].items()]
        dual_description = f"\n\n\nDual feature importance scores (Raw):   \t" \
                           f"{', '.join(dfi)}\n" \
                           f"Dual feature importance scores (Normalized): \t" \
                           f"{', '.join(dfw)}\n" \
                           f"Dual feature importance probability scores: \t" \
                           f"{', '.join(dfp)}\n"

        dual_labels = list(instance['dual']['probability_scores'].keys())
        dual_data = [[score] for score in list(instance['dual']['probability_scores'].values())]
        DIMEExplanation._visualize_cli_chart(
            title="",
            description=dual_description,
            labels=dual_labels,
            data=dual_data,
        )

    def visualize(self, token_limit: int = None) -> NoReturn:
        output_mode = self.explanation['config']['output_mode']

        main_description = f"Explanation Type: {self.explanation['config']['output_mode']}\n" \
                           f"Case Sensitive: {self.explanation['config']['case_sensitive']}\n" \
                           f"Global Metric: {self.explanation['config']['metric']}\n" \
                           f"N-grams: {self.explanation['config']['ngrams']}\n"

        if output_mode == OUTPUT_MODE_GLOBAL:
            self._visualize_global(
                title="",
                main_description=main_description,
                instance={},
                global_only=True,
                token_limit=token_limit
            )

        elif output_mode == OUTPUT_MODE_DUAL:
            if token_limit:
                logger.warning(f"Token limit specified will be ignored "
                               f"while visualizing Dual explanations")

            for instance in self.explanation['dual']:
                self._visualize_global(title='DUAL', main_description=main_description, instance=instance)
                self._visualize_dual(instance=instance)

        else:
            logger.error(f"The output_mode specified for the explanation "
                         f"is invalid. Could not visualize the given DIME "
                         f"explanation")
