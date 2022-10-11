import { Box, Snackbar } from "@mui/material";
import React, { Component } from "react";
import { configs } from "../../configs";
import ConfigForm from "../pageForms/ConfigForm";
import axios from "axios";
import MuiAlert from "@mui/material/Alert";

const Alert = React.forwardRef((props, ref) => (
  <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />
));

export default class ConfigTab extends Component {
  constructor(props) {
    super(props);
    this.state = {
      modelList: undefined,
      snackbarIsOpen: false,
      snackbarMessage: "",
      snackbarType: "success",
    };

    this.handleClose = this.handleClose.bind(this);
    this.fetchModels = this.fetchModels.bind(this);
  }

  componentDidMount() {
    this.fetchModels(null, this.props.appConfigs.dime_base_configs.models_path);
  }

  handleClose(event) {
    this.setState({ snackbarIsOpen: false });
  }

  fetchModels(event, modelsPath) {
    let payload = {
      models_path: modelsPath,
      origin: "models",
    };

    axios
      .post(`${configs.statsEndpoint}`, payload)
      .then(
        function (response) {
          console.log(response);
          if (response.data.status !== undefined) {
            if (response.data.status === "success") {
              this.setState({
                modelList: response.data.models_list,
              });
            } else {
              this.setState({
                snackbarIsOpen: true,
                snackbarMessage:
                  "No models found. Double check the models path in Configs",
                snackbarType: "error",
              });
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
          console.log(error.config);

          this.setState({
            modelList: undefined,
          });
        }.bind(this)
      );
  }

  render() {
    return (
      <>
        <Box
          className="tab-pane fade"
          id="config-tab-pane"
          role="tabpanel"
          aria-labelledby="config-tab"
          tabIndex="0"
        >
          <Box className="row p-3 justify-content-center">
            <Box className="alert app-alert mb-4" role="alert">
              <p className="white-to-black-ease">
                DIME configurations can be altered if required. Use either
                <kbd className="fs-6 kbd material-matt-black">
                  Restore Previous
                </kbd>{" "}
                to set the configs to the previous version or{" "}
                <kbd className="fs-6 kbd material-matt-black">Reset</kbd> to
                reset the configurations to the initial version.
              </p>
            </Box>
            <Box sx={{ marginTop: 5 }}>
              <ConfigForm
                appConfigs={this.props.appConfigs}
                secureUrl={this.props.secureUrl}
                modelList={this.state.modelList}
                fetchModels={this.fetchModels}
                fetchStats={this.props.fetchStats}
                showAppNotification={this.props.showAppNotification}
                hideAppNotification={this.props.hideAppNotification}
                scrollToTop={this.props.scrollToTop}
                fetchConfigs={this.props.fetchConfigs}
              />
            </Box>
          </Box>
        </Box>
        <Snackbar
          open={this.state.snackbarIsOpen}
          autoHideDuration={3000}
          onClose={this.handleClose}
          anchorOrigin={{
            vertical: `${configs.snackbarVerticalPosition}`,
            horizontal: `${configs.snackbarHorizontalPostion}`,
          }}
        >
          <Alert
            onClose={this.handleClose}
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
