import logging
import os
import platform
import signal
import subprocess
from datetime import datetime

from flask import (
    send_from_directory,
    request,
    send_file,
)
from flask_cors import cross_origin

from dime_xai.core.dime_core import load_explanation
from dime_xai.core.rasa_dime_explainer import RasaDIMEExplainer
from dime_xai.server.dime_api import blueprint
from dime_xai.server.dime_api.utils.server_configs import ServerConfigs
from dime_xai.server.dime_api.utils.statistics import (
    model_statistics,
    explanation_statistics
)
from dime_xai.shared.constants import (
    ExplanationType,
    Validity,
    ServerEnv,
    MODEL_TYPE_DIET,
    MODEL_TYPE_OTHER,
    DEFAULT_PERSIST_PATH,
    PROCESS_ID_NONE,
    ServerConfigType,
    PROCESS_QUEUE,
)
from dime_xai.shared.exceptions.dime_server_exceptions import (
    InvalidProcessIDException,
    ProcessTerminationException,
    ProcessAlreadyExistsException,
    InvalidRequestIDException,
    ProcessNotExistsException,
    ModelNotFoundException,
    ExplanationNotFoundException,
    InvalidExplanationSpecifiedException,
)
from dime_xai.utils import process_queue
from dime_xai.utils.io import file_exists
from dime_xai.utils.process_queue import kill_process_tree

logger = logging.getLogger(__name__)


@blueprint.route("/", strict_slashes=False, methods=['GET'])
@blueprint.route("/status", strict_slashes=False, methods=['GET'])
@cross_origin()
def api_status():
    logger.debug("Status API endpoint was called")
    return {
        "endpoint": "api",
        "status": "ok",
        "environment": "production",
    }


@blueprint.route("/explain", strict_slashes=False, methods=['POST'])
@cross_origin()
def explain():
    logger.debug("Explain API endpoint was called")
    request_id_for_exception_handling = None
    process_q = process_queue.ProcessQueue(data_source_path=PROCESS_QUEUE)

    try:
        request_data = request.get_json()
        app_env = request_data['app_env']

        # # handle these from frontend side
        # handle rest type modes
        # warn about global outputs
        model_type = request_data['model_type']
        data_instance = request_data['data_instance']
        output_mode = 'dual'

        if app_env == ServerEnv.STRICT_LOCAL:
            if model_type == MODEL_TYPE_DIET:
                rasa_dime_explainer = RasaDIMEExplainer(
                    models_path=request_data['models_path'],
                    model_name=request_data['model_name'],
                    testing_data_path=request_data['data_path'],
                    model_mode=request_data['model_mode'],
                    rasa_version=request_data['rasa_version'],
                    url=request_data['url_endpoint'],
                    data_instances=[data_instance],
                    ranking_length=request_data['ranking_length'],
                    case_sensitive=request_data['case_sensitive'],
                    metric=request_data['metric'],
                    output_mode=output_mode,
                )
                explanation_ = rasa_dime_explainer.explain(inspect=True)
                return {"status": "success", "explanation": explanation_.get_explanation(ExplanationType.QUIET)}, 200
            elif model_type == MODEL_TYPE_OTHER:
                return {"status": "error", "cause": "Non-DIET models are not supported yet"}, 200
        else:
            request_id = request_data['request_id']
            request_id_for_exception_handling = request_id
            data_instance = request_data['data_instance']

            # checking if request id is already
            # present in the process queue
            process_exists = process_q.check_existence(request_id=request_id)
            if process_exists:
                logger.error("Request Already Exists in the Process Queue")
                raise ProcessAlreadyExistsException()

            process_q.push(
                process_id=PROCESS_ID_NONE,
                request_id=request_id,
                timestamp=datetime.now().timestamp(),
                metadata=data_instance,
            )
            logger.debug(f"Pushed request {request_id} to process queue")

            if platform.system() == "Windows":
                sub_p = subprocess.Popen(
                    ["dime", "explain", "-r", f"{request_id}", "--quiet"],
                    shell=True,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                )
            else:
                sub_p = subprocess.Popen(
                    ["dime", "explain", "-r", f"{request_id}", "--quiet"],
                    shell=True,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    preexec_fn=os.setsid
                )

            # saving request and process id to process queue
            process_id = sub_p.pid
            process_q.update_pid(
                process_id=process_id,
                request_id=request_id,
                timestamp=datetime.now().timestamp()
            )
            logger.debug(f"Updated process queue of {request_id} with process id {process_id}")

            # grabbing stdout and stderr
            out, err = sub_p.communicate()
            out, err = out.decode("utf-8"), err.decode("utf-8")
            return_code = sub_p.returncode

            # setting return_code if errors are present
            explanation_result = ""
            if return_code == 1 or "error" in err:
                return_code = 1
            else:
                return_code = 0

            # retrieving explanation from process metadata
            if return_code == 0:
                explanation_result = process_q.get_metadata(request_id=request_id)

            # removing from process queue after process is executed
            process_q.remove(
                request_id=request_id
            )
            logger.debug(f"Process {process_id} under request id "
                         f"{request_id} was removed from process queue")

            logger.debug(f"Subprocess output: \n{out}")
            logger.debug(f"Subprocess errors: \n{err if err else 'None'}")
            logger.debug(f"Subprocess return code: \n{return_code}")

            response_payload = {
                "status": "success" if return_code == 0 else "error",
                "process_id": process_id,
                "request_id": request_id,
                "explanation": explanation_result,
            }
            return response_payload, 200
    except Exception as e:
        # removing the inserted process from the queue
        if request_id_for_exception_handling:
            process_q.remove(
                request_id=request_id_for_exception_handling
            )
        logger.error(f"Exception occurred while generating an Explanation "
                     f"for request id {request_id_for_exception_handling}. {e}")
        return {"status": "error"}, 200


@blueprint.route("/abort", strict_slashes=False, methods=['POST'])
@cross_origin()
def abort():
    logger.debug("Process abort API endpoint was called")

    try:
        request_data = request.get_json()
        process_q = process_queue.ProcessQueue(data_source_path=PROCESS_QUEUE)
        request_id = request_data["request_id"]

        if not request_id:
            raise InvalidRequestIDException()

        # check process existence
        process_exists = process_q.check_existence(request_id=request_id)
        if not process_exists:
            logger.error("Removing non-existing processes is not allowed")
            raise ProcessNotExistsException()

        # retrieving process_id
        process_id = process_q.get_pid(request_id=request_id)
        logger.debug(f"Confirmed the existence of the process {process_id} with the request id: {request_id}")

        if platform.system() == "Windows":
            kill_process_tree(int(process_id))
        else:
            os.killpg(os.getpgid(int(process_id)), signal.SIGTERM)
        logger.debug(f"Removed the existing process {process_id} with the request id: {request_id}")

        # updating the process queue
        process_q.remove(request_id=request_id)
        logger.debug(f"Removed process from queue. [process id: {process_id}, request id: {request_id}]")
        return {"status": "success", "process_id": process_id}, 200
    except InvalidProcessIDException as e:
        logger.error(f"Invalid process ID received. {e}")
        return {"status": "error"}
    except ProcessTerminationException as e:
        logger.error(f"Process termination error. {e}")
        return {"status": "error"}
    except Exception as e:
        logger.error(f"Unknown process termination exception {e}")
        return {"status": "error"}


@blueprint.route("/stats", strict_slashes=False, methods=['POST'])
@cross_origin()
def stats():
    try:
        request_data = request.get_json()
        origin = request_data['origin']
        if origin == "models":
            model_sizes_list = model_statistics(request_data=request_data, reverse=True)
            return {
                       "status": "success",
                       "models_list": model_sizes_list,
                   }, 200
        elif origin == "explanations":
            explanations_list = explanation_statistics(reverse=True)
            return {
                       "status": "success",
                       "explanations_list": explanations_list
                   }, 200
        elif origin == "dashboard":
            model_sizes_list = model_statistics(request_data=request_data, reverse=True)
            explanations_list = explanation_statistics(reverse=True)
            return {
                       "status": "success",
                       "explanations": len(explanations_list),
                       "models": len(model_sizes_list),
                   }, 200
        else:
            model_sizes_list = model_statistics(request_data=request_data, reverse=True)
            explanations_list = explanation_statistics(reverse=True)
            return {
                       "status": "success",
                       "models": len(model_sizes_list),
                       "explanations": len(explanations_list),
                       "models_list": model_sizes_list,
                       "explanations_list": explanations_list
                   }, 200
    except Exception as e:
        logger.error(f"Exception occurred while getting stats. {e}")
        return {"status": "error"}, 200


@blueprint.route("/model", strict_slashes=False, methods=['DELETE'])
@cross_origin()
def model():
    logger.debug("Models API endpoint was called")
    if request.method == "DELETE":
        try:
            request_data = request.get_json()
            models_path = request_data["models_path"]
            model_name = request_data["model_name"]
            model_path = os.path.join(models_path, model_name)

            if not file_exists(file_path=model_path):
                logger.error("Specified model does not exist")
                raise ModelNotFoundException()

            os.remove(path=model_path)
            logger.debug(f"Deleted the specified model {model_name}")

            return {"status": "success", "model_name": model_name}, 200
        except Exception as e:
            logger.error(f"Exception occurred while deleting the model. {e}")
            return {"status": "error"}, 200
    else:
        return {"status": "error"}, 200


@blueprint.route("/explanation", strict_slashes=False, methods=['GET', 'POST', 'DELETE'])
@cross_origin()
def explanation():
    logger.debug("Explanations API endpoint was called")
    explanations_path = DEFAULT_PERSIST_PATH
    if request.method == "DELETE":
        logger.debug(f"Deleting an explanation...")
        try:
            request_data = request.get_json()
            explanation_name = request_data["explanation_name"]
            explanation_path = os.path.join(explanations_path, explanation_name)

            if not file_exists(file_path=explanation_path):
                logger.error("Specified explanation does not exist")
                raise ExplanationNotFoundException()

            os.remove(path=explanation_path)
            logger.debug(f"Deleted the specified explanation {explanation_name}")

            return {"status": "success", "explanation_name": explanation_name}, 200
        except Exception as e:
            logger.error(f"Exception occurred while deleting the explanation. {e}")
            return {"status": "error"}, 200
    elif request.method == "POST":
        logger.debug(f"Uploading an explanation...")
        try:
            request_data = request.get_json()
            explanation_ = request_data["explanation"]
            explanation_obj = load_explanation(explanation=explanation_)
            explanation_obj.persist()
            logger.debug(f"Explanation uploaded as {explanation_obj.file_name}")

            return {"status": "success", "explanation_name": explanation_obj.file_name}, 200
        except Exception as e:
            logger.error(f"Exception occurred while uploading the explanation. {e}")
            return {"status": "error"}, 200
    else:
        logger.debug(f"Downloading an explanation...")
        try:
            explanation_name = request.args.get("explanation_name", "")
            if not explanation_name:
                raise InvalidExplanationSpecifiedException()

            logger.debug(f"Sending {explanation_name} file...")
            return send_file(
                path_or_file=os.path.join(os.getcwd(), explanations_path, explanation_name),
                as_attachment=True
            )
        except Exception as e:
            logger.error(f"Exception occurred while downloading the explanation. {e}")
            return {"status": "error"}, 200


@blueprint.route("/explanation/visualize", strict_slashes=False, methods=["GET"])
@cross_origin()
def visualize_explanation():
    logger.debug("Explanation visualize API endpoint was called")
    try:
        explanation_name = request.args.get("explanation_name", "")
        if not explanation_name:
            raise InvalidExplanationSpecifiedException()

        explanation_ = load_explanation(explanation=explanation_name)
        metadata = explanation_.get_explanation(output_type=ExplanationType.QUIET)
        return {
                   "status": "success",
                   "explanation": metadata
               }, 200
    except Exception as e:
        logger.error(f"Exception occurred while getting stats. {e}")
        return {"status": "error"}, 200


@blueprint.route("/configs", strict_slashes=False, methods=['GET', 'POST'])
@cross_origin()
def configs():
    logger.debug("Configs API endpoint was called")
    server_configs = ServerConfigs()

    if request.method == 'POST':
        try:
            request_data = request.get_json()
            updated_configs = request_data['updated_configs']
            validate_status, validate_res = server_configs.validate(configs=updated_configs)
            if not validate_status:
                return {"status": Validity.INVALID, "metadata": validate_res}, 200

            server_configs.update_and_persist(
                updated_configs=updated_configs,
                validate=False
            )
            return {"status": Validity.VALID}, 200

        except Exception as e:
            logger.error(f"Exception occurred while updating server configs. {e}")
            return {"status": "error", "validations": None}, 200
    else:
        try:
            server_configs_json = server_configs.retrieve(
                config_type=ServerConfigType.JSON,
                custom_configs=True
            )
            return {"status": "success", "configs": server_configs_json}
        except Exception as e:
            logger.error(f"Exception occurred while retrieving the server configurations. {e}")
            return {"status": "error"}


@blueprint.route("/<path:path>", strict_slashes=False)
@cross_origin()
def api_static_files(path):
    logger.debug("API static files are served")
    if path != 'dime_gray.png':
        return {"status": "error", "message": "Not Authorized"}, 403
    return send_from_directory(directory=blueprint.static_folder, path=path), 200
