import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Text, NoReturn, List, Dict, Union, Optional

import requests
from rasa.cli.utils import get_validated_path
from rasa.model import get_model, get_model_subdirectories
from rasa.nlu.model import Interpreter
from requests import Response
from tqdm import tqdm

from dime_xai.shared.constants import (
    RASA_REST_ENDPOINT_PARSE,
    MODEL_MODE_LOCAL,
    NLU_FALLBACK_TAG,
)
from dime_xai.shared.exceptions.dime_core_exceptions import (
    RESTModelLoadException,
    ModelFingerprintPersistException,
)
from dime_xai.shared.exceptions.dime_io_exceptions import (
    ModelNotFoundException,
    ModelLoadException,
)
from dime_xai.shared.model.model import Model
from dime_xai.utils.fingerprint import generate_model_fingerprint
from dime_xai.utils.io import (
    exit_dime,
    get_latest_model_name,
    file_exists,
)

logger = logging.getLogger(__name__)


class RASAModel(Model):
    """
    Acts as a container that holds a local RASA model or
    holds the URL for a REST RASA model. Can parse both
    supervised and unsupervised data as instances or batches
    """
    def __init__(
            self,
            model_mode: Text,
            models_path: Text = None,
            model_name: Text = None,
            url: Text = None,
    ) -> NoReturn:
        self._model_mode = model_mode
        self._models_path = models_path
        self._model_name = model_name
        self._url = url
        self._nlu_model = None
        self._metadata = dict()
        self._fingerprint = None
        if model_mode == MODEL_MODE_LOCAL:
            self._load_model()

    def _load_model(
            self,
            model_name: Text = None
    ) -> NoReturn:
        """
        An internal method that loads a local RASA model and returns it.
        This method is responsible for extracting RASA model metadata and
        generate model fingerprint after loading a valid RASA model

        Args:
            model_name: A valid RASA model name that resides in the
            './models' directory of the DIME project root

        Returns:
            no return
        """
        if model_name:
            if file_exists(os.path.join(self._models_path, model_name)):
                self._model_name = model_name
            else:
                raise ModelNotFoundException(f"Could not find the RASA model `{model_name}` in the specified "
                                             f"location, `{self._models_path}`")

        try:
            base_model_path = get_validated_path(
                os.path.join(self._models_path, self._model_name),
                "model"
            )
            sub_model_path = get_model(base_model_path)
            _, nlu_model = get_model_subdirectories(sub_model_path)
            self._nlu_model = Interpreter.load(nlu_model)
        except Exception:
            raise ModelLoadException(f"An error occurred while loading "
                                     f"the RASA model '{model_name}'")

        if self._nlu_model:
            self._metadata = self._nlu_model.model_metadata.metadata
            try:
                self._fingerprint = generate_model_fingerprint(
                    model_metadata=self._metadata,
                    persist=True
                )
                logger.info(f"RASA Model fingerprint: {self._fingerprint}")

            except ModelFingerprintPersistException as e:
                logger.error(f"Failed to persist the model fingerprint. {e}")

            logger.info(f'Successfully loaded RASA model: {self._model_name}')
        else:
            logger.info(f'Error occurred while loading the RASA model: {self._model_name}')
            exit_dime()

    def load_latest_model(self) -> NoReturn:
        """
        Loads the latest local RASA model available in the
        './models' directory of the DIME project root.

        Returns:
            no return
        """
        latest_model_name = get_latest_model_name(
            models_path=self._models_path
        )
        self._load_model(model_name=latest_model_name)

    def _process_supervised_output(
            self, data_instance: Dict,
            model_response: Union[Dict, Response]
    ) -> Dict:
        """
        Generates the output dictionary for predictions obtained
        from local or REST RASA models. Uses instance variables,
        thus, is for internal use only

        Args:
            data_instance: data instance dictionary with labeled
                intent. Must have the keys, 'intent' and 'example'.

            model_response:  output provided by the RASA model.
                Model response is a dictionary for local models
                and is an HTTP Response if the model is REST.

        Returns:
            Dict: A dictionary that contains 'intent', 'example',
                'predicted intent', 'predicted confidence',
                'intent_confidence', and 'intent_ranking'.
        """
        if self._model_mode == MODEL_MODE_LOCAL:
            output = {
                'example': data_instance['example'],
                'intent': data_instance['intent'],
                'predicted_intent': model_response['intent']['name'] or NLU_FALLBACK_TAG,
                'predicted_confidence': model_response['intent']['confidence'],
                'intent_confidence': [x['confidence']
                                      for x
                                      in model_response['intent_ranking']
                                      if x['name'] == data_instance['intent']][0]
                if 'intent_ranking' in model_response else 0.0,
                'intent_ranking': model_response['intent_ranking']
                if 'intent_ranking' in model_response else []
            }
        else:
            output = {
                'example': data_instance['example'],
                'intent': data_instance['intent'],
                'predicted_intent': model_response.json()['intent']['name'] or NLU_FALLBACK_TAG,
                'predicted_confidence': model_response.json()['intent']['confidence'],
                'intent_confidence': [x['confidence']
                                      for x
                                      in model_response.json()['intent_ranking']
                                      if x['name'] == data_instance['intent']][0]
                if 'intent_ranking' in model_response.json() else 0.0,
                'intent_ranking': model_response.json()['intent_ranking']
                if 'intent_ranking' in model_response.json() else []
            }
        return output

    def _process_supervised_batch_output(self, model_response) -> List:
        if self._model_mode == MODEL_MODE_LOCAL:
            output = [{'example': response[0],
                       'intent': response[1],
                       'predicted_intent': response[2].result()['intent']['name'] or NLU_FALLBACK_TAG,
                       'predicted_confidence': response[2].result()['intent']['confidence'],
                       'intent_confidence': [x['confidence'] for x
                                             in response[2].result()['intent_ranking']
                                             if x['name'] == response[1]][0]
                       if 'intent_ranking' in response[2].result() else 0.0,
                       'intent_ranking': response[2].result()['intent_ranking']
                       if 'intent_ranking' in response[2].result() else []
                       }
                      for response in model_response]
        else:
            output = [{'example': response[0],
                       'intent': response[1],
                       'predicted_intent': response[2].result().json()['intent']['name'] or NLU_FALLBACK_TAG,
                       'predicted_confidence': response[2].result().json()['intent']['confidence'],
                       'intent_confidence': [x['confidence'] for x
                                             in response[2].result().json()['intent_ranking']
                                             if x['name'] == response[1]][0]
                       if 'intent_ranking' in response[2].result().json() else 0.0,
                       'intent_ranking': response[2].result()['intent_ranking']
                       if 'intent_ranking' in response[2].result().json() else []
                       }
                      for response in model_response]
        return output

    def _process_unsupervised_output(self, data_instance: Text, model_response: Union[Dict, Response]) -> Dict:
        if self._model_mode == MODEL_MODE_LOCAL:
            output = {
                'example': data_instance,
                'predicted_intent': model_response['intent']['name'] or NLU_FALLBACK_TAG,
                'predicted_confidence': model_response['intent']['confidence'],
                'intent_ranking': model_response['intent_ranking']
                if 'intent_ranking' in model_response else []
            }
        else:
            output = {
                'example': data_instance,
                'predicted_intent': model_response.json()['intent']['name'] or NLU_FALLBACK_TAG,
                'predicted_confidence': model_response.json()['intent']['confidence'],
                'intent_ranking': model_response.json()['intent_ranking']
                if 'intent_ranking' in model_response.json() else []
            }
        return output

    def _process_unsupervised_batch_output(self, model_response) -> List:
        if self._model_mode == MODEL_MODE_LOCAL:
            output = [{'example': response[0],
                       'predicted_intent': response[1].result()['intent']['name'] or NLU_FALLBACK_TAG,
                       'predicted_confidence': response[1].result()['intent']['confidence'],
                       'intent_ranking': response[1].result()['intent_ranking']
                       if 'intent_ranking' in response[1].result() else []
                       }
                      for response in model_response]
        else:
            output = [{'example': response[0],
                       'predicted_intent': response[1].result().json()['intent']['name'] or NLU_FALLBACK_TAG,
                       'predicted_confidence': response[1].result().json()['intent']['confidence'],
                       'intent_ranking': response[1].result().json()['intent_ranking']
                       if 'intent_ranking' in response[1].result().json() else []
                       }
                      for response in model_response]
        return output

    def _process_tagged_supervised_batch_output(
            self,
            model_response: List,
    ) -> List:
        if self._model_mode == MODEL_MODE_LOCAL:
            output = [{'tag': response[0]['tag'],
                       'intent': response[0]['intent'],
                       'example': response[0]['example'],
                       'predicted_intent': response[1].result()['intent']['name'] or NLU_FALLBACK_TAG,
                       'predicted_confidence': response[1].result()['intent']['confidence'],
                       'intent_confidence': [x['confidence'] for x
                                             in response[1].result()['intent_ranking']
                                             if x['name'] == response[0]['intent']][0]
                       if 'intent_ranking' in response[1].result() else 0.0,
                       'intent_ranking': response[1].result()['intent_ranking']
                       if 'intent_ranking' in response[1].result() else []
                       }
                      for response in model_response]
        else:
            output = [{'tag': response[0]['tag'],
                       'intent': response[0]['intent'],
                       'example': response[0]['example'],
                       'predicted_intent': response[1].result().json()['intent']['name'] or NLU_FALLBACK_TAG,
                       'predicted_confidence': response[1].result().json()['intent']['confidence'],
                       'intent_confidence': [x['confidence'] for x
                                             in response[1].result().json()['intent_ranking']
                                             if x['name'] == response[1]][0]
                       if 'intent_ranking' in response[1].result().json() else 0.0,
                       'intent_ranking': response[1].result()['intent_ranking']
                       if 'intent_ranking' in response[1].result().json() else []
                       }
                      for response in model_response]
        return output

    def _parse_rest(self, data_instance: Text) -> Response:
        try:
            request_body = {'text': data_instance}
            response = requests.post(url=self._url + RASA_REST_ENDPOINT_PARSE, json=request_body)
            if response.status_code != 200:
                raise Exception

            return response
        except Exception:
            raise RESTModelLoadException(f"Exception occurred while parsing the RASA REST model")

    def _parse_batch_rest(
            self,
            dataset: Union[Dict, List],
            is_supervised: bool = True,
            description: Text = ""
    ) -> List:
        rasa_responses = list()
        try:
            if is_supervised:
                tqdm_dataset = tqdm(dataset.items())
                tqdm_dataset.set_description(f"{description}")
                for intent, examples in tqdm_dataset:
                    with ThreadPoolExecutor(max_workers=os.cpu_count() * 5) as executor:
                        for example in examples:
                            future = executor.submit(
                                self._parse_rest,
                                example,
                            )
                            rasa_responses.append([example, intent, future])
                return self._process_supervised_batch_output(rasa_responses)
            else:
                tqdm_dataset = tqdm(dataset)
                for example in tqdm_dataset:
                    with ThreadPoolExecutor(max_workers=os.cpu_count() * 5) as executor:
                        future = executor.submit(
                            self._parse_rest,
                            example,
                        )
                        rasa_responses.append([example, future])
                return self._process_unsupervised_batch_output(rasa_responses)
        except Exception as e:
            logger.error(f"Exception occurred. {e}")
            exit_dime()

    def _parse_tagged_batch(
            self,
            dataset: List,
            description: Text = "",
            use_threading: bool = True,
    ) -> List:
        """
        Parses a tagged supervised dataset passed as a List using
        a REST Rasa model. Uses threading if specified to parse
        large datasets

        Args:
            dataset: dataset as a List of Dicts with 'tag', 'intent' and 'example' as keys
            description: A description to be shown as the progress bar prefix

        Returns: The list of parsed instance dictionaries with keys 'tag', 'intent', 'example',
        'predicted_intent', 'predicted_confidence', and 'intent_ranking'

        """
        rasa_responses = list()

        if self._model_mode == MODEL_MODE_LOCAL:
            parsing_function = self._parse_local
        else:
            parsing_function = self._parse_rest

        try:
            tqdm_dataset = tqdm(dataset)
            tqdm_dataset.set_description(f"{description}")
            if use_threading:
                for instance in tqdm_dataset:
                    example = instance['example']
                    with ThreadPoolExecutor(max_workers=os.cpu_count() * 5) as executor:
                        future = executor.submit(
                            parsing_function,
                            example,
                        )
                        rasa_responses.append([instance, future])
            else:
                raise NotImplementedError()
            return self._process_tagged_supervised_batch_output(rasa_responses)

        except NotImplementedError:
            raise NotImplementedError()
        except Exception as e:
            raise Exception(f"Exception occurred. {e}")

    def _parse_local(self, data_instance: Text) -> Dict:
        return self._nlu_model.parse(data_instance)

    def _parse_batch_local(
            self,
            dataset: Union[Dict, List],
            is_supervised: bool = True,
            description: Text = ""
    ) -> List:
        local_responses = list()
        try:
            if is_supervised:
                tqdm_dataset = tqdm(dataset.items())
                tqdm_dataset.set_description(f"{description}")
                for intent, examples in tqdm_dataset:
                    with ThreadPoolExecutor(max_workers=os.cpu_count() * 5) as executor:
                        for example in examples:
                            future = executor.submit(
                                self._parse_local,
                                example
                            )
                            local_responses.append([example, intent, future])
                return self._process_supervised_batch_output(local_responses)
            else:
                tqdm_dataset = tqdm(dataset)
                for example in tqdm_dataset:
                    with ThreadPoolExecutor(max_workers=os.cpu_count() * 5) as executor:
                        future = executor.submit(
                            self._parse_local,
                            example
                        )
                        local_responses.append([example, future])
                return self._process_unsupervised_batch_output(local_responses)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as e:
            logger.error(f"Exception occurred. {e}")
            exit_dime()

    def parse_supervised(self, data_instance: Dict) -> Dict:
        if self._model_mode == MODEL_MODE_LOCAL:
            raw_response = self._parse_local(
                data_instance=data_instance['example']
            )
        else:
            raw_response = self._parse_rest(
                data_instance=data_instance['example']
            )
        return self._process_supervised_output(
            data_instance=data_instance,
            model_response=raw_response
        )

    def parse_supervised_batch(self, data_instances: Union[List, Dict], description: Text = "") -> List:
        if isinstance(data_instances, Dict):
            if self._model_mode == MODEL_MODE_LOCAL:
                model_response = self._parse_batch_local(
                    dataset=data_instances,
                    description=description
                )
                return model_response
            else:
                bot_responses = self._parse_batch_rest(
                    dataset=data_instances,
                    description=description
                )
                return bot_responses
        elif isinstance(data_instances, List):
            model_response = self._parse_tagged_batch(
                dataset=data_instances,
                description=description
            )
            return model_response

    def parse_unsupervised(self, data_instance: Text) -> Dict:
        if self._model_mode == MODEL_MODE_LOCAL:
            raw_response = self._parse_local(data_instance=data_instance)
        else:
            raw_response = self._parse_rest(data_instance=data_instance)
        return self._process_unsupervised_output(data_instance=data_instance, model_response=raw_response)

    def parse_unsupervised_batch(self, data_instances: List, description: Text = "") -> List:
        if self._model_mode == MODEL_MODE_LOCAL:
            model_response = self._parse_batch_local(
                dataset=data_instances,
                is_supervised=False,
                description=description
            )
            return model_response
        else:
            bot_responses = self._parse_batch_rest(
                dataset=data_instances,
                is_supervised=False,
                description=description
            )
            return bot_responses

    def get_model_metadata(self) -> Optional[Dict]:
        return self._metadata

    def get_fingerprint(self) -> Optional[Text]:
        return self._fingerprint

    def test_diet_compatibility(self, intents: List) -> bool:
        if self._model_mode == MODEL_MODE_LOCAL:
            raw_response = self._parse_local(data_instance='test')
            diet_labels = [x['name'] for x in raw_response['intent_ranking']] \
                if 'intent_ranking' in raw_response else []

        else:
            raw_response = self._parse_rest(data_instance='test')
            diet_labels = [x['name'] for x in raw_response.json()['intent_ranking']] \
                if 'intent_ranking' in raw_response.json() else []

        intents.append(NLU_FALLBACK_TAG)
        unique_labels = sorted(list(set(intents)))
        diet_labels.append(NLU_FALLBACK_TAG)
        unique_diet_labels = sorted(list(set(diet_labels)))

        if unique_diet_labels == unique_labels:
            return True

        return False
