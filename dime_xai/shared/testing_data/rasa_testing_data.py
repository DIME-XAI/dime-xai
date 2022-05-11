import logging
from typing import List, Optional, Text, NoReturn, Union, Dict

import pandas as pd
from rasa.shared.nlu.training_data.loading import load_data
from rasa.shared.nlu.training_data.message import Message

from dime_xai.shared.exceptions.dime_io_exceptions import EmptyNLUDatasetException
from dime_xai.shared.testing_data.testing_data import TestingData
from dime_xai.utils.fingerprint import generate_dataset_fingerprint
from dime_xai.utils.text_preprocessing import (
    bag_of_words,
    get_all_tokens,
    lowercase_list,
)
from dime_xai.shared.constants import (
    DEFAULT_CASE_SENSITIVE_MODE,
    DEFAULT_DATAFRAME_MODE,
    NLU_FALLBACK_TAG
)
from dime_xai.utils.io import (
    get_rasa_testing_data,
    get_unique_list,
)

logger = logging.getLogger(__name__)


class RASATestingData(TestingData):
    def __init__(
            self,
            testing_data_dir: Text = None,
            case_sensitive: bool = DEFAULT_CASE_SENSITIVE_MODE,
            from_rasa: bool = False,
    ):
        super().__init__(testing_data_dir, case_sensitive)
        self._from_rasa = from_rasa
        self._initialize_testing_data()

    def _initialize_testing_data(self) -> NoReturn:
        if self._from_rasa:
            self._rasa_testing_data = load_data(resource_name=self._testing_data_dir)
            if self._rasa_testing_data.is_empty():
                raise EmptyNLUDatasetException("Failed to retrieve NLU data.")

            testing_data = dict()
            nlu_examples = self._rasa_testing_data.nlu_examples
            for message in nlu_examples:
                msg: Message = message
                if msg.data['intent'] not in testing_data:
                    testing_data[msg.data['intent']] = [msg.data['text']]
                else:
                    testing_data[msg.data['intent']].append(msg.data['text'])

            if not self.case_sensitive:
                testing_data = {k: lowercase_list(v) for k, v in testing_data.items()}

            self._testing_data = testing_data

        else:
            self._testing_data = get_rasa_testing_data(
                testing_data_dir=self._testing_data_dir,
                case_sensitive=self.case_sensitive,
            )

        if not self._testing_data:
            raise EmptyNLUDatasetException("Failed to retrieve NLU data.")

        all_instances = self.get_instances()
        dataset_vocabulary = bag_of_words(
            instances=all_instances,
            merge=True
        )
        self._vocabulary = sorted(get_unique_list(dataset_vocabulary)) if dataset_vocabulary else []
        self._vocabulary_size = len(self._vocabulary)
        self._tokens = get_all_tokens(instances=all_instances, merge=True)
        self._fingerprint = self._rasa_testing_data.fingerprint() if self._from_rasa else \
            generate_dataset_fingerprint(self._testing_data)

        logger.info(f'Total number of intents: {self.get_intent_size()}')
        logger.info(f'Total number of data instances: {self.get_instance_size()}')
        logger.info(f'Vocabulary size: {self._vocabulary_size}')

    def get_testing_data(
            self,
            as_dataframe: bool = DEFAULT_DATAFRAME_MODE,
    ) -> Union[Dict, pd.DataFrame]:
        testing_data = self._testing_data

        if as_dataframe:
            dataset = pd.DataFrame(columns=['intent', 'example'])

            for intent, examples in testing_data.items():
                for example in examples:
                    dataset_row = [intent, example]
                    dataset.loc[len(dataset)] = dataset_row

            dataset.drop_duplicates(inplace=True)
            dataset.reset_index(inplace=True)
            dataset.drop(columns=['index'], inplace=True)
            return dataset
        else:
            return testing_data

    def get_testing_data_as_rasa(self) -> Optional[List[Message]]:
        return self._rasa_testing_data.nlu_examples if self._from_rasa else []

    def get_instances(
            self,
            intent: Text = None,
    ) -> Optional[List]:
        all_instances = list()
        if intent:
            if intent in self._testing_data:
                all_instances = self._testing_data[intent]
            else:
                logger.error("Could not find the given intent name in testing data. Please input a valid intent name.")
        else:
            for key, value in self._testing_data.items():
                all_instances += value
        return get_unique_list(all_instances)

    def get_instance_size(
            self,
            intent: Text = None,
    ) -> Optional[int]:
        filtered_instances = self.get_instances(intent=intent)
        return len(filtered_instances)

    def get_intents(self) -> Optional[List]:
        if not self._testing_data:
            return []
        intents = list(self._testing_data.keys())
        intents.append(NLU_FALLBACK_TAG)
        return intents

    def get_intent_size(self) -> Optional[int]:
        if not self._testing_data:
            return 0

        return len(self._testing_data.keys())

    def get_tokens(self) -> Optional[List]:
        return self._tokens

    def get_token_size(self) -> Optional[int]:
        return len(self._tokens)

    def get_vocabulary(self) -> Optional[List]:
        return self._vocabulary

    def get_vocabulary_size(self) -> Optional[int]:
        vocabulary = self.get_vocabulary()
        return len(vocabulary)

    def get_fingerprint(self) -> Optional[Text]:
        return self._fingerprint
