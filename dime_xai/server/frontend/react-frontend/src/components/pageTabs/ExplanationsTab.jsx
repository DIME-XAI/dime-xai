import React, { Component } from "react";
import axios, { CanceledError } from "axios";
import { v4 as uuidv4 } from "uuid";
import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";
import { Box, Button, Stack, ToggleButton } from "@mui/material";
import { LoadingButton } from "@mui/lab";
import {
  RestartAlt,
  MarkChatRead,
  Cancel,
  Keyboard,
  Save,
} from "@mui/icons-material";
import ExplanationDetails from "../explanation/ExplanationDetails";
import GlobalExplanation from "../explanation/GlobalExplanation";
import DualExplanation from "../explanation/DualExplanation";
import { configs, localStorageKeys } from "../../configs";
import KeyboardInterface from "../keyboardInterface/KeyboardInterface";

const Alert = React.forwardRef((props, ref) => (
  <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />
));

export default class ExplanationsTab extends Component {
  constructor(props) {
    super(props);
    this.state = {
      dataInstanceValue: props.appConfigs.dime_base_configs.data_instance[0],
      previousDataInstanceValue:
        props.appConfigs.dime_base_configs.data_instance[0],
      dataInstanceHelperText: "Invalid Data Instance",
      dataInstanceValidity: "notset",
      explainButtonInProgress: false,
      explanation: undefined,
      explanationRequestId: undefined,
      snackbarIsOpen: false,
      snackbarMessage: "",
      snackbarType: "success",
      selectedLanguage:
        localStorage.getItem(`${localStorageKeys.DimeSelectedLang}`) || "en",
      keyboardEnabled: props.appConfigs.custom_configs.keyboard_enabled,
    };

    // refs
    this.cancelTokenExplainRequest = React.createRef();

    // button handlers
    this.handleExplain = this.handleExplain.bind(this);
    this.handleReset = this.handleReset.bind(this);
    this.handleSnackbarClose = this.handleSnackbarClose.bind(this);
    this.handleAbort = this.handleAbort.bind(this);

    // keyboard handlers
    this.handleDataInstanceChange = this.handleDataInstanceChange.bind(this);
    this.handleDataInstanceChangeText =
      this.handleDataInstanceChangeText.bind(this);
    this.handleLanguage = this.handleLanguage.bind(this);
    this.handleDataInstanceChange = this.handleDataInstanceChange.bind(this);
    this.handleInputFocus = this.handleInputFocus.bind(this);
    this.handleLangSwitch = this.handleLangSwitch.bind(this);
  }

  handleDataInstanceChange(event) {
    this.setState({
      dataInstanceValue: event.target.value,
    });
  }

  handleDataInstanceChangeText(text) {
    this.setState({
      dataInstanceValue: text,
    });
  }

  handleLanguage(language) {
    this.setState(
      {
        selectedLanguage: language,
      },
      () => {
        localStorage.setItem(`${localStorageKeys.DimeSelectedLang}`, language);
        this.dataInstanceRef.handleLanguage(language);
        this.dataInstanceRef.handleInputFocus();
      }
    );
  }

  handleInputFocus(event) {
    this.dataInstanceRef.handleInputFocus();
  }

  handleLangSwitch(event) {
    let language = this.state.selectedLanguage === "en" ? "si" : "en";
    localStorage.setItem(`${localStorageKeys.DimeSelectedLang}`, language);
    this.setState(
      {
        selectedLanguage: language,
      },
      () => {
        this.dataInstanceRef.handleLanguage(language);
        this.dataInstanceRef.handleInputFocus();
      }
    );
  }

  handleSnackbarClose(event) {
    this.setState({ snackbarIsOpen: false });
  }

  validateDataInstance(dataInstance) {
    if (dataInstance.toString().trim() === "") {
      this.setState({
        snackbarMessage: "Invalid Data Instance",
        snackbarType: "error",
        snackbarIsOpen: true,
        dataInstanceValidity: "invalid",
        dataInstanceHelperText: "Data Instance must be longer than 1 Token",
      });
      return false;
    } else if (dataInstance.toString().trim().split(" ").length < 2) {
      this.setState({
        snackbarMessage: "Invalid Data Instance",
        snackbarType: "warning",
        snackbarIsOpen: true,
        dataInstanceValidity: "invalid",
        dataInstanceHelperText:
          "Data Instances shorter than 2 Tokens are less Interpretable",
      });
      return false;
    }

    return true;
  }

  handleExplain(event) {
    this.props.hideAppNotification();

    // validate
    if (!this.validateDataInstance(this.state.dataInstanceValue)) {
      return;
    }

    let request_id = uuidv4();
    let payload = {
      data_instance: this.state.dataInstanceValue,
      request_id: request_id,
      app_env: this.props.appConfigs.custom_configs.app_env,
      model_type: this.props.appConfigs.dime_base_configs.model_type,
      headers: { "Content-Type": "application/json" },
    };

    console.log("payload", payload);

    this.setState({
      explainButtonInProgress: true,
      explanation: undefined,
      snackbarIsOpen: false,
      explanationRequestId: request_id,
      dataInstanceValidity: "notset",
    });

    this.cancelTokenExplainRequest.current = axios.CancelToken.source();

    console.log("[request id] " + request_id);

    axios
      .post(configs.explainEndpoint, payload, {
        cancelToken: this.cancelTokenExplainRequest.current.token,
      })
      .then(
        function (response) {
          console.log(response);
          if (response.data.status !== undefined) {
            if (response.data.status === "success") {
              let explanation = JSON.parse(response.data.explanation);
              this.setState({
                snackbarMessage: "Explanation generated successfully!",
                snackbarType: "success",
                snackbarIsOpen: true,
                explanation: explanation,
                explainButtonInProgress: false,
                previousDataInstanceValue: this.state.dataInstanceValue,
              });
              this.props.fetchStats();
            } else {
              throw new Error("Unexpected error");
            }
          } else {
            throw new Error("Unexpected response");
          }
        }.bind(this)
      )
      .catch(
        function (error) {
          console.log(error);
          let notifyTitle = "DIME Explanation Error";
          let notifyBody =
            "An unknown error occurred while generating the explanation. Please try again a bit later.";
          let snackbarMessage =
            "An unknown error occurred while requesting the explanation";
          let snackbarType = "error";

          if (error instanceof CanceledError) {
            notifyBody = "Explanation Request Aborted!";
            snackbarMessage = notifyBody;
            snackbarType = "warning";
          } else if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            notifyBody = "Failed to obtain a valid explanation";
            snackbarMessage = notifyBody;
          } else if (error.request) {
            // The request was made but no response was received
            console.log(error.request);
            notifyBody = "Explanation was never received";
            snackbarMessage = notifyBody;
          } else {
            // Something happened in setting up the request that triggered an Error
            console.log("Error:", error.message);
            notifyBody = "Failed to request the explanation";
            snackbarMessage = notifyBody;
          }
          console.log(error.config);

          this.setState({
            snackbarMessage: snackbarMessage,
            snackbarType: snackbarType,
            snackbarIsOpen: true,
            explainButtonInProgress: false,
          });

          this.props.scrollToTop();
          this.props.showAppNotification(notifyTitle, notifyBody);
        }.bind(this)
      );
  }

  handleReset(event) {
    this.dataInstanceRef.handleInputReset();
    this.dataInstanceRef.setText(this.state.previousDataInstanceValue);

    this.setState({
      explanation: undefined,
      dataInstanceValidity: "notset",
    });
  }

  handleAbort(event) {
    let payload = {
      request_id: this.state.explanationRequestId,
      headers: {
        "Content-Type": "application/json",
      },
    };
    console.log("[abort request id] " + payload.request_id);
    axios
      .post(configs.abortExplainEndpoint, payload)
      .then(
        function (response) {
          console.log(response);
          if (response.data.status !== undefined) {
            if (response.data.status === "success") {
              this.setState({
                explainButtonInProgress: false,
                explanationRequestId: undefined,
              });

              this.cancelTokenExplainRequest.current.cancel();
              console.log("request aborted!");
            } else {
              throw new Error("Abort request was discarded");
            }
          } else {
            throw new Error("Failed to send abort request");
          }
        }.bind(this)
      )
      .catch(
        function (error) {
          console.log(error);
          this.setState({
            snackbarMessage: "Request aborting failed",
            snackbarType: "error",
            snackbarIsOpen: true,
            explainButtonInProgress: false,
          });
        }.bind(this)
      );
  }

  render() {
    return (
      <>
        <Box
          className="tab-pane fade show active"
          id="exp-tab-pane"
          role="tabpanel"
          aria-labelledby="exp-tab"
          tabIndex="0"
        >
          <Box className="row p-3 pb-0 justify-content-center">
            <Box className="alert app-alert mb-4" role="alert">
              <p className="white-to-black-ease">
                Provide a sentence to be explained and make sure it is longer
                than a single word. Then, simply tap{" "}
                <kbd className="fs-6 kbd material-matt-black">Explain</kbd>{" "}
                button to get the explanation. If required to change the current
                DIME configurations, plese navigate to the{" "}
                <kbd
                  className="fs-6 kbd material-matt-black app-cursor-pointer"
                  onClick={this.props.handleConfigTab}
                >
                  Configurations
                </kbd>{" "}
                tab.
              </p>
            </Box>
            <Box sx={{ marginTop: 3 }}>
              <Box className="row justify-content-center mb-4 mt-4 model-comman">
                <Box className="col-md-5 col-lg-3">
                  <label
                    htmlFor="basic-url"
                    className="form-label white-to-black-ease"
                  >
                    Data Instance: <br />
                    <span className="text-muted">
                      (Sentence to be explained)
                    </span>
                  </label>
                </Box>
                <Box className="col-md-7 col-lg-5">
                  <Box className="input-group input-group-dark">
                    <Box className="d-flex mb-3 p-0 w-100">
                      <span
                        className="input-group-text material-icons"
                        id="dataInstanceSpan"
                      >
                        chat
                      </span>
                      <KeyboardInterface
                        interface={"textfield"}
                        placeholder="Data Instance"
                        value={
                          this.props.appConfigs.dime_base_configs
                            .data_instance[0]
                        }
                        className={"w-100"}
                        disableUnderline={true}
                        defaultLanguage={
                          this.props.appConfigs.custom_configs.keyboard_enabled
                            ? localStorage.getItem(
                                `${localStorageKeys.DimeSelectedLang}`
                              ) || "si"
                            : "en"
                        }
                        ref={(messageRef) =>
                          (this.dataInstanceRef = messageRef)
                        }
                        handleChange={this.handleDataInstanceChange}
                        handleTextChange={this.handleDataInstanceChangeText}
                        handleShortcut={this.handleLanguage}
                        handleEnter={this.handleExplain}
                        enableShortcuts={
                          this.props.appConfigs.custom_configs.keyboard_enabled
                            ? true
                            : false
                        }
                        shortcutKey={81}
                        error={
                          this.state.dataInstanceValidity === "invalid"
                            ? true
                            : false
                        }
                        helperText={
                          this.state.dataInstanceValidity === "invalid"
                            ? this.state.dataInstanceHelperText
                            : ""
                        }
                      />
                    </Box>
                  </Box>
                </Box>
                <Box className="col-md-12 col-lg-8">
                  {this.state.keyboardEnabled && (
                    <ToggleButton
                      sx={{
                        width: "80px",
                        "&.MuiToggleButton-root": { color: "black" },
                      }}
                      value="check"
                      selected={
                        this.state.selectedLanguage === "en" ? true : false
                      }
                      onChange={(e) => {
                        this.handleLangSwitch(e);
                      }}
                    >
                      <Keyboard sx={{ marginRight: "4px" }} />
                      {this.state.selectedLanguage === "en" ? "en" : "si"}
                    </ToggleButton>
                  )}
                  {this.state.explainButtonInProgress ? (
                    <Stack direction="row" spacing={1} className={"float-end"}>
                      <LoadingButton
                        loading
                        loadingPosition="start"
                        startIcon={<Save />}
                        variant="outlined"
                        className="float-end explanation-loading-button"
                        size="1.5rem"
                        sx={{ height: "2.4rem" }}
                        disabled
                      >
                        Explain
                      </LoadingButton>
                      {this.props.appConfigs.custom_configs.app_env ===
                      "strict_local" ? (
                        <Button
                          variant="outlined"
                          className="float-end app-button"
                          sx={{ border: "none", "&:hover": { border: "none" } }}
                          startIcon={<RestartAlt />}
                          disabled
                        >
                          Reset
                        </Button>
                      ) : (
                        <Button
                          variant="outlined"
                          className="float-end app-button app-button-red ms-2"
                          sx={{ border: "none", "&:hover": { border: "none" } }}
                          startIcon={<Cancel />}
                          onClick={this.handleAbort}
                        >
                          Abort
                        </Button>
                      )}
                    </Stack>
                  ) : (
                    <Stack direction="row" spacing={1} className={"float-end"}>
                      <Button
                        variant="outlined"
                        className="float-end app-button app-button-steel"
                        sx={{ border: "none", "&:hover": { border: "none" } }}
                        startIcon={<MarkChatRead />}
                        onClick={this.handleExplain}
                      >
                        Explain
                      </Button>
                      <Button
                        variant="outlined"
                        className="float-end app-button app-button-red"
                        sx={{ border: "none", "&:hover": { border: "none" } }}
                        startIcon={<RestartAlt />}
                        onClick={this.handleReset}
                      >
                        Reset
                      </Button>
                    </Stack>
                  )}
                </Box>
                {this.state.explanation === undefined ? (
                  <Box></Box>
                ) : (
                  <Box className="row mt-4 pt-4 mb-0 model-common justify-content-center">
                    <Box className="col-12 col-lg-8">
                      <ExplanationDetails data={this.state.explanation} />
                      <GlobalExplanation
                        color="purple"
                        data={this.state.explanation}
                      />
                      <DualExplanation
                        color="green"
                        data={this.state.explanation}
                      />
                    </Box>
                  </Box>
                )}
              </Box>
            </Box>
          </Box>
        </Box>
        <Snackbar
          open={this.state.snackbarIsOpen}
          autoHideDuration={3000}
          onClose={this.handleSnackbarClose}
          anchorOrigin={{
            vertical: `${configs.snackbarVerticalPosition}`,
            horizontal: `${configs.snackbarHorizontalPostion}`,
          }}
        >
          <Alert
            onClose={this.handleSnackbarClose}
            severity={this.state.snackbarType}
            sx={{ width: "100%" }}
          >
            {this.state.snackbarMessage.toString()}
          </Alert>
        </Snackbar>
      </>
    );
  }
}
