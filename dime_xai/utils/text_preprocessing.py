from typing import Text, Optional, List, Union, Dict
from copy import deepcopy
import regex

from dime_xai.utils.io import get_unique_list


def tokenize(instance: Text) -> Optional[List]:
    """
    Tokenizes a whitespace tokenize-able language.
    Tokenizing steps are the same as in Rasa
    WhitespaceTokenizer component

    Args:
        instance: whitespace tokenize-able string

    Returns:
        list of tokens or None
    """
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


def bag_of_words(
        instances: Union[Text, List],
        merge: bool = False
) -> Optional[Union[List, Dict]]:
    """
    Returns the bag of words of a string or
    a list of strings. Bag of words representation
    contains the unique list of words in a string or
    a list of strings

    Args:
        instances: a string or a list of strings
        merge: merges a list of strings as a single string is True.
        returns bag of words for each string in a list as a dictionary
        if set to False

    Returns:
        bag of words list for a string or a merged list of strings [List],
            bag of words list per each string in a list of strings [Dict], or None
    """
    instances_copy = deepcopy(instances)
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
    """
    Counts the number of instances of a token
    within a list of tokens passed

    Args:
        token_list: all tokens as a list
        token: token to get the number of instances

    Returns:
        number of instances as an int
    """
    return token_list.count(token)


def get_all_tokens(
        instances: Union[Text, List],
        merge: bool = False
) -> Optional[Union[List, Dict]]:
    """
    Returns all tokens present in a single string instance
    or a list of string instances

    Args:
        instances: single string instance or a list of strings
        merge: if True, mergers a list of strings passed as a single string

    Returns:
        for a single string, returns the list of tokens.
            for a list of unmerged strings, returns the list
            of tokens per each string instance as a dictionary
    """
    instances_copy = deepcopy(instances)
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
    """
    Removes instances of a specified token
    from a single string instance

    Args:
        instance: string instance where the token should be removed from
        token: token to be removed

    Returns:
        token removed single string instance
    """
    instance = regex.sub(token + " ", "", instance)
    instance = regex.sub(" " + token, "", instance)
    return regex.sub(token, "", instance)


def remove_token_from_dataset(
        testing_data: Union[List, Dict],
        token: Text
) -> Union[List, Dict]:
    """
    Removes all instances of a specified
    token from the given dataset

    Args:
        testing_data: data instances as a list, or dictionary.
            If passed as dictionary, instances should be mentioned
            as a list under 'example' key under each intent/class

        token: token to be removed from the dataset

    Returns:
        token removed list or dictionary
    """
    testing_data_copy = deepcopy(testing_data)

    if isinstance(testing_data_copy, Dict):
        for intent, examples in testing_data_copy.items():
            testing_data_copy[intent] = [remove_token(example, token) for example in examples]
        return testing_data_copy
    else:
        for instance in testing_data_copy:
            instance['example'] = remove_token(instance=instance['example'], token=token)
        return testing_data_copy


def lowercase_list(instances_list: List) -> List:
    """
    lower-cases a list of strings

    Args:
        instances_list: list of strings to be lower-cased

    Returns:
        lower-cased list of strings
    """
    return [str.lower(instance) for instance in instances_list]


def order_dict(
        dict_to_order: Dict,
        order_by_key: bool = False,
        reverse: bool = False,
) -> Optional[Dict]:
    """
    Recursively orders a dictionary either
    by keys or values if comparable

    Args:
        dict_to_order: dictionary to be ordered
        order_by_key: orders by key if True, else orders by value
        reverse: orders in the ascending order if False,
            else orders in the descending order

    Returns:
        ordered dictionary, or None
    """
    if not dict_to_order:
        return None

    if order_by_key:
        index = 0
    else:
        index = 1

    ordered_dict = {
        k: v for k, v in sorted(
            dict_to_order.items(),
            key=lambda x: x[index],
            reverse=reverse)
    }

    for k, v in ordered_dict.items():
        if isinstance(v, Dict):
            ordered_dict[k] = order_dict(v, order_by_key=order_by_key, reverse=reverse)

    return ordered_dict
