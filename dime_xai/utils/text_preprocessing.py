from typing import Text, Optional, List, Union, Dict
import regex

from dime_xai.utils.io import get_unique_list


def tokenize(instance: Text) -> Optional[List]:
    if not instance:
        return None

    # same logic from rasa tokenizer
    # to inherit the same tokenizing logic
    words = regex.sub(
        # there is a space or an end of a string after it
        r"[^\w#@&]+(?=\s|$)|"
        # there is a space or beginning of a string before it
        # not followed by a number
        r"(\s|^)[^\w#@&]+(?=[^0-9\s])|"
        # not in between numbers and not . or @ or & or - or #
        # e.g. 10'000.00 or blabla@gmail.com
        # and not url characters
        r"(?<=[^0-9\s])[^\w._~:/?#\[\]()@!$&*+,;=-]+(?=[^0-9\s])",
        " ",
        instance,
    ).split()

    tokens = [w for w in words if w]
    return tokens


def bag_of_words(instances: Union[Text, List], merge: bool = False) -> Optional[Union[List, Dict]]:
    instances_copy = instances
    if not instances_copy:
        return None

    if merge and isinstance(instances_copy, List):
        instances_copy = ' '.join(instances_copy)

    if isinstance(instances_copy, List):
        instance_vocabulary = dict()
        for instance in instances_copy:
            bow = list()
            bow += tokenize(instance=instance)
            bow = sorted(get_unique_list(bow)) if bow else []
            instance_vocabulary[instance] = bow
        return instance_vocabulary

    elif isinstance(instances_copy, Text):
        vocabulary = list()
        vocabulary += tokenize(instance=instances_copy)
        vocabulary = sorted(get_unique_list(vocabulary)) if vocabulary else []
        return vocabulary


def get_token_count(token_list: List, token: Text) -> int:
    return token_list.count(token)


def get_all_tokens(instances: Union[Text, List], merge: bool = False) -> Optional[Union[List, Dict]]:
    instances_copy = instances
    if not instances_copy:
        return None

    if merge and isinstance(instances_copy, List):
        instances_copy = ' '.join(instances_copy)

    if isinstance(instances_copy, List):
        instance_vocabulary = dict()
        for instance in instances_copy:
            bow = list()
            bow += tokenize(instance=instance)
            instance_vocabulary[instance] = bow
        return instance_vocabulary

    elif isinstance(instances_copy, Text):
        vocabulary = list()
        vocabulary += tokenize(instance=instances_copy)
        return vocabulary


def remove_token(instance: Text, token: Text) -> Text:
    instance = regex.sub(token + " ", "", instance)
    instance = regex.sub(" " + token, "", instance)
    return regex.sub(token, "", instance)


def remove_token_from_dataset(testing_data: Union[List, Dict], token: Text) -> Union[List, Dict]:
    testing_data_copy = testing_data.copy()

    if isinstance(testing_data_copy, Dict):
        for intent, examples in testing_data_copy.items():
            testing_data_copy[intent] = [remove_token(example, token) for example in examples]
        return testing_data_copy
    else:
        for instance in testing_data_copy:
            instance['example'] = remove_token(instance=instance['example'], token=token)
        return testing_data_copy


def lowercase_list(instances_list: List) -> List:
    return [str.lower(instance) for instance in instances_list]


def order_dict(
        dict_to_order: Dict,
        order_by_key: bool = False,
        reverse: bool = False,
) -> Optional[Dict]:
    if not dict_to_order:
        return None

    if order_by_key:
        index = 0
    else:
        index = 1

    return {
        k: v for k, v in sorted(
            dict_to_order.items(),
            key=lambda x: x[index],
            reverse=reverse)
    }
