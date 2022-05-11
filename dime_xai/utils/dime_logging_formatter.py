import logging
import re
from copy import copy
from logging import Formatter

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


class DIMELoggingFormatter(Formatter):

    def __init__(self, format_str):
        Formatter.__init__(self, format_str)

    def format(self, record):
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
            exception_details = e
            return Formatter.format(self, record_cpy)


class MaxLevelFilter(logging.Filter):
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno < self.level
