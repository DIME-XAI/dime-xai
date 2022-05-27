import logging
import re
from copy import copy
from logging import Formatter
from typing import Text

from dime_xai.shared.constants import (
    TermColor,
)

MAPPING = {
    'DEBUG': 35,  # white
    'INFO': 34,  # cyan
    'WARNING': 33,  # yellow
    'ERROR': 38,  # red
    'CRITICAL': 31,  # white on red bg
    'RESET': 12,
    'GRAY': 32,
}

PREFIX = '\033['
SUFFIX = '\033[0m'

logger = logging.getLogger(__name__)


class DIMELoggingFormatter(Formatter):
    """
    A custom logging formatter for DIME
    """

    def __init__(self, format_str):
        Formatter.__init__(self, format_str)

    def format(self, record) -> Text:
        """
        Formats a given logging record by
        wrapping it with required color codes

        Args:
            record: logging record to be wrapped

        Returns:
            formatted logging record
        """
        record_cpy = copy(record)
        try:
            formatted_record = Formatter.format(self, record_cpy)
            level_name = record_cpy.levelname
            colored_level_name = TermColor.LIGHTGREEN + str(level_name) + TermColor.END_C

            message = " - " + record_cpy.message
            asc_time = record_cpy.asctime
            name = record_cpy.name

            colored_message = TermColor.WHITE + str(message) + TermColor.END_C
            colored_asc_time = TermColor.WHITE + str(asc_time) + TermColor.END_C
            colored_name = TermColor.CYAN + str(name) + TermColor.END_C

            formatted_record = TermColor.WHITE + str(formatted_record) + TermColor.END_C

            formatted_record = re.sub(
                asc_time + "\t" + level_name + "\t" + name + message,
                colored_asc_time + "\t" + colored_level_name + "\t" + colored_name + colored_message,
                formatted_record
            )

            return formatted_record
        except Exception as e:
            logger.debug(e)
            return Formatter.format(self, record_cpy)


class MaxLevelFilter(logging.Filter):
    """
    Sets a filter to the logging level
    """
    def __init__(self, level):
        super().__init__(name='')
        self.level = level

    def filter(self, record) -> bool:
        """
        filters a given logging record and
        returns True if logging levels falls
        under the specified max logging level

        Args:
            record: logging record to be inspected

        Returns:
            True if logging level is less than max
                logging level, or else False
        """
        return record.levelno < self.level
