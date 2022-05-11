import logging
from typing import Dict

from flask import (
    Flask,
    jsonify,
    render_template,
)
from werkzeug.exceptions import HTTPException

from dime_xai.shared.constants import (
    DIMEConfig,
)
from dime_xai.shared.exceptions.dime_server_exceptions import (
    DimeServerNotFoundException,
    DimeServerException,
    DIMEBaseException,
)

logger = logging.getLogger(__name__)
app = Flask(__name__)

INITIAL_SERVER_CONFIGS = dict()


@app.route("/")
def dashboard():
    logger.info("Dashboard served.")
    return render_template("dashboard/dime_main.html")


@app.route("/status")
def status():
    logger.info("Status route was called.")
    return jsonify([{"server": "dime_server"}, {"status": "ok"}])


@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return render_template("error/dime_error_http.html", error=e, title=f"DIME HTTP {e.code} Error",)

    # now you're handling non-HTTP exceptions only
    return render_template("error/dime_error_http.html", error=e, title=f"DIME Server {e.code} Error")


if __name__ == "__main__":
    app.run(debug=True)


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
        logger.info(f"Starting DIME server at http://{self.host}:{self.port}")
        try:
            global INITIAL_SERVER_CONFIGS
            INITIAL_SERVER_CONFIGS = self.configs

            app.run(
                host=self.host,
                port=self.port,
                debug=self.debug_mode
            )
        except OSError:
            logger.exception(f"Possible permission exception while starting the DIMEServer.")
        except DimeServerNotFoundException:
            logger.exception(f"An unknown exception occurred while invoking the DIMEServer.")
        except DimeServerException:
            logger.exception(f"Specific::DIMEServer.")
        except DIMEBaseException:
            logger.exception(f"Base::DIMEServer.")
        except Exception as e:
            logger.exception(f"Base::broad::DIMEServer. more info: {e}")
        return
