import logging
import os
from typing import Dict

from waitress import serve as waitress_serve

from dime_xai.server import create_app
from dime_xai.shared.constants import (
    DIMEConfig,
    DIME_ASCII_LOGO,
    ServerEnv,
)
from dime_xai.shared.exceptions.dime_core_exceptions import DIMECoreException
from dime_xai.shared.exceptions.dime_server_exceptions import (
    DIMEServerNotFoundException,
    DIMEServerException,
    DIMEBaseException,
)
from dime_xai.utils.io import exit_dime
from dime_xai.utils.process_queue import create_in_memory_process_queue

logger = logging.getLogger(__name__)


class DIMEServer:
    def __init__(
            self,
            configs: Dict = None,
            debug_mode: bool = None,
    ):
        self.configs = configs
        self.port = configs[DIMEConfig.MAIN_KEY_SERVER][DIMEConfig.SUB_KEY_SERVER_PORT]
        self.debug_mode = debug_mode
        self.host = configs[DIMEConfig.MAIN_KEY_SERVER][DIMEConfig.SUB_KEY_SERVER_HOST]

    def run(self) -> None:
        logger.info(f"Starting DIME server at http://{self.host}:{self.port}/")
        try:
            import json
            app_config = {
                "DIME": self.configs,
                "APP_THEME": os.environ.get("APP_THEME") or "dark",
                "APP_ENV": os.environ.get("APP_ENV") or "prod",
                "SINHALA_ENABLED": os.environ.get("SINHALA_ENABLED") or True,
            }
            create_in_memory_process_queue()

            # # Disabled due to attaching server cache
            # # with the process queue
            # from dime_xai.utils.server_cache import create_in_memory_server_cache
            # create_in_memory_server_cache()

            if self.debug_mode:
                logger.warning("Deploying DIME Server in development mode...")
                os.environ["APP_ENV"] = ServerEnv.DEV
                app = create_app(configs=app_config)
                app.run(
                    host=self.host,
                    port=self.port,
                    debug=self.debug_mode
                )
            else:
                logger.info("Deploying DIME Server in production mode...")
                print(DIME_ASCII_LOGO)
                waitress_serve(create_app(configs=app_config), host=self.host, port=self.port)

                # # Run as a shell command if required
                # import subprocess
                # subprocess.run(["waitress-serve", f"--host={self.host}",
                #                 f"--port={self.port}", "dime_xai.server.dime_server:run"])

        except DIMEServerNotFoundException:
            logger.exception(f"An unknown exception occurred while invoking the DIMEServer")
        except DIMECoreException:
            logger.exception(f"Core::DIMEServer")
        except DIMEServerException:
            logger.exception(f"Specific::DIMEServer")
        except DIMEBaseException:
            logger.exception(f"Base::DIMEServer")
        except KeyboardInterrupt:
            logger.info(f"Gracefully terminating DIME Server...")
            exit_dime()
        except OSError:
            logger.exception(f"Possible permission exception while starting the DIMEServer")
        except Exception as e:
            logger.exception(f"Base::broad::DIMEServer. more info: {e}")
        return
