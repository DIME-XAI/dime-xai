import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Text, NoReturn, List, Dict, Union, Optional
import requests
from requests import Response

from rasa.cli.utils import get_validated_path
from rasa.model import get_model, get_model_subdirectories
from rasa.nlu.model import Interpreter
from tqdm import tqdm

from dime_xai.shared.exceptions.dime_core_exceptions import RESTModelLoadException
from dime_xai.shared.model.model import Model
from dime_xai.utils.fingerprint import generate_model_fingerprint
from dime_xai.utils.io import (
    exit_dime,
    get_latest_model_name,
    file_exists,
)
from dime_xai.shared.constants import (
    RASA_REST_ENDPOINT_PARSE,
    MODEL_MODE_LOCAL, NLU_FALLBACK_TAG,
)
from dime_xai.shared.exceptions.dime_io_exceptions import (
    ModelNotFoundException,
    ModelLoadException,
)

logger = logging.getLogger(__name__)


class RASAModel(Model):
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

    def _load_model(self, model_name: Text = None) -> NoReturn:
        """
        This loads the Rasa NLU interpreter. It is able to apply all NLU
        pipeline steps to a text that you provide it.
        """
        if model_name:
            if file_exists(os.path.join(self._models_path, model_name)):
                self._model_name = model_name
            else:
                raise ModelNotFoundException(f"Could not find the RASA model `{model_name}` in the specified "
                                             f"location, `{self._models_path}`")

        try:
            base_model_path = get_validated_path(os.path.join(self._models_path, self._model_name), "model")
            sub_model_path = get_model(base_model_path)
            _, nlu_model = get_model_subdirectories(sub_model_path)
            self._nlu_model = Interpreter.load(nlu_model)
        except Exception:
            raise ModelLoadException(f"An error occurred while loading "
                                     f"the RASA model '{model_name}")

        if self._nlu_model:
            self._metadata = self._nlu_model.model_metadata.metadata
            self._fingerprint = generate_model_fingerprint(
                model_metadata=self._metadata,
                persist=True
            )
            logger.info(f'Successfully loaded RASA model: {self._model_name}')
        else:
            logger.info(f'Error occurred while loading the RASA model: {self._model_name}')
            exit_dime()

    def _load_latest_model(self) -> NoReturn:
        latest_model_name = get_latest_model_name(models_path=self._models_path)
        self._load_model(model_name=latest_model_name)

    def _process_supervised_output(self, data_instance: Dict, model_response: Union[Dict, Response]) -> Dict:
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
                if 'intent_ranking' in model_response else 0.0
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
                if 'intent_ranking' in model_response.json() else 0.0
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
                       if 'intent_ranking' in response[2].result() else 0.0
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
                       if 'intent_ranking' in response[2].result().json() else 0.0
                       }
                      for response in model_response]
        return output

    def _process_unsupervised_output(self, data_instance: Text, model_response: Union[Dict, Response]) -> Dict:
        if self._model_mode == MODEL_MODE_LOCAL:
            output = {
                'example': data_instance,
                'predicted_intent': model_response['intent']['name'] or NLU_FALLBACK_TAG,
                'predicted_confidence': model_response['intent']['confidence'],
            }
        else:
            output = {
                'example': data_instance,
                'predicted_intent': model_response.json()['intent']['name'] or NLU_FALLBACK_TAG,
                'predicted_confidence': model_response.json()['intent']['confidence'],
            }
        return output

    def _process_unsupervised_batch_output(self, model_response) -> List:
        if self._model_mode == MODEL_MODE_LOCAL:
            output = [{'example': response[0],
                       'predicted_intent': response[1].result()['intent']['name'] or NLU_FALLBACK_TAG,
                       'predicted_confidence': response[1].result()['intent']['confidence']}
                      for response in model_response]
        else:
            output = [{'example': response[0],
                       'predicted_intent': response[1].result().json()['intent']['name'] or NLU_FALLBACK_TAG,
                       'predicted_confidence': response[1].result().json()['intent']['confidence']}
                      for response in model_response]
        return output

    def _parse_rest(self, data_instance: Text) -> Response:
        try:
            request_body = {'text': data_instance}
            return requests.post(url=self._url + RASA_REST_ENDPOINT_PARSE, json=request_body)
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
            raw_response = self._parse_local(data_instance=data_instance['example'])
        else:
            raw_response = self._parse_rest(data_instance=data_instance['example'])
        return self._process_supervised_output(data_instance=data_instance, model_response=raw_response)

    def parse_supervised_batch(self, data_instances: Dict, description: Text = "") -> List:
        if self._model_mode == MODEL_MODE_LOCAL:
            model_response = self._parse_batch_local(dataset=data_instances, description=description)
            return model_response
        else:
            bot_responses = self._parse_batch_rest(dataset=data_instances, description=description)
            return bot_responses

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
                if 'intent_ranking' in raw_response else []

        intents.append(NLU_FALLBACK_TAG)
        unique_labels = sorted(list(set(intents)))
        diet_labels.append(NLU_FALLBACK_TAG)
        unique_diet_labels = sorted(list(set(diet_labels)))

        if unique_diet_labels == unique_labels:
            return True

        return False
