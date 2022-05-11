import argparse
import logging
import os
import sys
from typing import Optional

from dime_xai.cli.dimecli import DimeCLIExplainer, DimeCLIVisualizer
from dime_xai.server.dimeserver import DIMEServer
from dime_xai.shared.constants import (
    InterfaceType,
    TermColor,
    DEFAULT_PERSIST_PATH,
    OUTPUT_MODE_GLOBAL,
    OUTPUT_MODE_DUAL,
    OUTPUT_MODE_LOCAL,
    PACKAGE_VERSION_LONG,
    Metrics,
)
from dime_xai.utils.config import get_default_configs
from dime_xai.utils.dime_logging_formatter import (
    DIMELoggingFormatter,
    MaxLevelFilter,
)
from dime_xai.utils.io import (
    set_cli_color,
    dir_exists,
    update_sys_path,
    exit_dime,
    file_exists,
)
from dime_xai.utils.scaffold import DIMEInit

logger = logging.getLogger()
update_sys_path(os.getcwd())

formatter = DIMELoggingFormatter(format_str='%(asctime)s\t%(levelname)s\t%(name)s - %(message)s')
logging_out = logging.StreamHandler(sys.stdout)
logging_err = logging.StreamHandler(sys.stderr)
logging_out.setFormatter(formatter)
logging_err.setFormatter(formatter)
logging_out.addFilter(MaxLevelFilter(logging.WARNING))
logging_out.setLevel(logging.DEBUG)
logging_err.setLevel(logging.WARNING)
logger.addHandler(logging_out)
logger.addHandler(logging_err)
logger.setLevel(level=logging.INFO)

# disabling unwanted tf cuda logs
# for conda environments, manually set env var
# conda env config vars set TF_CPP_MIN_LOG_LEVEL=2
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


def create_argument_parser():
    """
    Parses the arguments passed to dime_xai through dime CLI tool.
    Returns:
        argparse.ArgumentParser()
    """

    parser = argparse.ArgumentParser(prog="dime", description="starts DIME CLI")
    subparsers = parser.add_subparsers(help='desired DIME interface to run [cli/server]', dest="subparser_name")

    parser.add_argument(
        "-v",
        "--version",
        action='version',
        version=PACKAGE_VERSION_LONG,
        help="prints the DIME version info.",
    )

    parser_server = subparsers.add_parser(
        name="server",
        help='run DIME server, a web-based visualization tool for DIME.'
    )
    parser_server.add_argument(
        "-p",
        "--port",
        type=int,
        help="the port to start the dime server at.",
    )
    parser_server.add_argument(
        "--debug",
        action="store_true",
        help="sets the logging level to debug mode from info and flask server debug mode to true.",
    )

    parser_explainer = subparsers.add_parser(
        name="explain",
        help='run DIME CLI explainer, a terminal-based explainer tool for DIME.'
    )
    parser_explainer.add_argument(
        "-i",
        "--instance",
        type=str,
        default=None,
        help="data instance to generate explanations.",
    )
    parser_explainer.add_argument(
        "-m",
        "--metric",
        type=str,
        choices=[Metrics.F1_SCORE, Metrics.ACCURACY, Metrics.CONFIDENCE],
        default=None,
        help="metric used to calculate the global feature importance.",
    )
    parser_explainer.add_argument(
        "-o",
        "--output",
        type=str,
        choices=[OUTPUT_MODE_GLOBAL, OUTPUT_MODE_DUAL, OUTPUT_MODE_LOCAL],
        help="data instance to generate explanations.",
    )
    parser_explainer.add_argument(
        "--case",
        action="store_true",
        default=None,
        help="preserves the case sensitivity of data.",
    )
    parser_explainer.add_argument(
        "--no-case",
        dest="case",
        action="store_false",
        help="does not preserve the case sensitivity of data.",
    )
    parser_explainer.add_argument(
        "--debug",
        action="store_true",
        help="sets the logging level to debug mode from info.",
    )

    parser_visualizer = subparsers.add_parser(
        name="visualize",
        help='run DIME CLI visualizer, a terminal-based '
             'visualization tool for already generated '
             'DIME explanations.'
    )
    parser_visualizer.add_argument(
        "-e",
        "--explanation",
        type=str,
        default=None,
        help="explanation file name for generating visualizations.",
    )
    parser_visualizer.add_argument(
        "-l",
        "--limit",
        type=int,
        default=None,
        help="limit the number of tokens visualized in the descending order.",
    )
    parser_visualizer.add_argument(
        "--debug",
        action="store_true",
        help="sets the logging level to debug mode from info.",
    )

    parser_init = subparsers.add_parser(
        name="init",
        help='create init dir structure for a new explanation process.'
    )
    parser_init.add_argument(
        "--debug",
        action="store_true",
        help="sets the logging level to debug mode from info.",
    )
    parser_init.add_argument(
        "--quite",
        action="store_true",
        help="initializes a starter dime project without prompting the user for a project location.",
    )
    return parser


def _set_logging_level(debug: bool = False):
    if debug:
        logger.setLevel(level=logging.DEBUG)
    else:
        logger.setLevel(level=logging.INFO)


def run_dime_cli() -> Optional:
    try:
        logger.debug("Running main DIME CLI.")
        arg_parser = create_argument_parser()
        cmdline_args = arg_parser.parse_args()
        interface = cmdline_args.subparser_name

        if not interface:
            arg_parser.print_help()
            logger.error("Please specify a valid positional arg out of \'explain\', \'visualize\', "
                         "\'server\', \'init\' to use dime CLI.")
            return

        if str(interface).lower() == InterfaceType.INTERFACE_INIT:
            quite = cmdline_args.quite
            debug_mode = cmdline_args.debug
            if debug_mode:
                _set_logging_level(debug=debug_mode)

            try:
                if not quite:
                    print(set_cli_color(text_content="👋🏽 Hi there! Welcome to DIME.", color=TermColor.LIGHTGREEN))
                    dest_dir = input(set_cli_color(
                        text_content="In which directory do you want to "
                                     "initialize DIME? [Default: Current Directory]: ",
                        color=TermColor.LIGHTGREEN
                    ))
                else:
                    dest_dir = "."

                if dest_dir and not dir_exists(dir_path=dest_dir):
                    logger.error("Directory name should only contain "
                                 "valid chars and it should not be a path.")
                    return

                dime_init = DIMEInit()
                dime_init.build_scaffold(dest_path=dest_dir)
            except KeyboardInterrupt:
                print("")
                logger.error("Non-graceful termination occurred. [Ctrl+C]")

        elif str(interface).lower() == InterfaceType.INTERFACE_SERVER:
            server_port = cmdline_args.port
            debug_mode = cmdline_args.debug
            if debug_mode:
                _set_logging_level(debug=debug_mode)

            configs = get_default_configs(
                interface=InterfaceType.INTERFACE_SERVER,
                server_port=server_port,
            )

            if not configs:
                logger.error("Failed to retrieve default dime "
                             "configs. DIME CLI will be terminated.")
                return

            dime_server = DIMEServer(
                configs=configs,
                debug_mode=debug_mode or False,
            )
            dime_server.run()

        elif str(interface).lower() == InterfaceType.INTERFACE_CLI_EXPLAINER:
            data_instance = cmdline_args.instance
            output_mode = cmdline_args.output
            global_metric = cmdline_args.metric
            case_sensitive = cmdline_args.case
            debug_mode = cmdline_args.debug

            if debug_mode:
                _set_logging_level(debug=debug_mode)

            configs = get_default_configs(
                interface=InterfaceType.INTERFACE_CLI,
                data_instance=data_instance,
                output_mode=output_mode,
                global_metric=global_metric,
                case_sensitive=case_sensitive,
            )
            if not configs:
                logger.error("Failed to retrieve default dime "
                             "configs. DIME CLI will be terminated.")
                return

            dime_cli_explainer = DimeCLIExplainer(
                configs=configs,
            )
            dime_cli_explainer.run()

        elif str(interface).lower() == InterfaceType.INTERFACE_CLI_VISUALIZER:
            explanation_file = cmdline_args.explanation
            limit = cmdline_args.limit
            debug_mode = cmdline_args.debug

            if debug_mode:
                _set_logging_level(debug=debug_mode)

            if not explanation_file:
                logger.error("A DIME explanation file must be "
                             "specified to generate visualizations.")
                return

            if not file_exists(os.path.join(DEFAULT_PERSIST_PATH, explanation_file)):
                logger.error("The specified DIME explanation file does not exist "
                             "in the dime_explanations directory. DIME CLI will be terminated.")
                return

            dime_cli_visualizer = DimeCLIVisualizer(
                file_name=explanation_file,
                limit=limit,
            )
            dime_cli_visualizer.run()

        else:
            logger.error('One or more incorrect CLI arguments detected. '
                         'Refer "dime -h" to view allowed arguments')
            return
    except KeyboardInterrupt:
        logger.info(f"Gracefully terminating DIME CLI...")


if __name__ == "__main__":
    logger.error("This script cannot be directly executed. "
                 "please use the 'dime' CLI instead.")
    exit_dime(exit_code=1)
