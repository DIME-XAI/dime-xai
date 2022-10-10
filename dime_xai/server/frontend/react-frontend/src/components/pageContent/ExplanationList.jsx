import React, { Component } from "react";
import { DialogTitle, Divider, Drawer, List } from "@mui/material";
import axios, { CanceledError } from "axios";
import { configs } from "../../configs";
import ExplanationDetails from "../explanation/ExplanationDetails";
import GlobalExplanation from "../explanation/GlobalExplanation";
import DualExplanation from "../explanation/DualExplanation";
import { Box } from "@mui/system";
import ExplanationPaginator from "./ExplanationPaginator";
import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";

const Alert = React.forwardRef((props, ref) => (
  <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />
));

export default class ExplanationList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      snackbarIsOpen: false,
      snackbarMessage: "",
      snackbarType: "success",
      deleteInProgress: false,
      visualizeInProgress: false,
      downloadInProgress: false,
      activeExplanation: undefined,
      activeVisualization: undefined,
      drawerIsOpen: false,
    };

    this.handleDelete = this.handleDelete.bind(this);
    this.handleDownload = this.handleDownload.bind(this);
    this.handleVisualize = this.handleVisualize.bind(this);
    this.setActiveExplanation = this.setActiveExplanation.bind(this);
    this.getActiveExplanation = this.getActiveExplanation.bind(this);
    this.handleSnackbarClose = this.handleSnackbarClose.bind(this);
    this.generateModalId = this.generateModalId.bind(this);
    this.handleDrawerClose = this.handleDrawerClose.bind(this);
  }

  handleSnackbarClose(event) {
    this.setState({ snackbarIsOpen: false });
  }

  handleDrawerClose(event) {
    this.setState({
      drawerIsOpen: false,
      activeVisualization: undefined,
    });
  }

  generateModalId(explanationName) {
    try {
      explanationName = explanationName.toString();
      explanationName = explanationName.replace(".json", "");
      explanationName = explanationName.replace(
        /[#_~`@$%^&*()\-+=/\\. ,?"':;]/g,
        ""
      );
      return `expid${explanationName}`;
    } catch (err) {
      console.log("Exception occurred while generating Modal ID");
      return "";
    }
  }

  generateExplanationDate(explanationName) {
    try {
      explanationName = explanationName.toString();
      explanationName = explanationName.replace("dime_results_", "");
      explanationName = explanationName.replace(".json", "");
      explanationName = explanationName.split("_");

      let year = explanationName[0].substring(0, 4);
      let month = explanationName[0].substring(4, 6);
      let date = explanationName[0].substring(6, 8);
      let hour = explanationName[1].substring(0, 2);
      let minute = explanationName[1].substring(2, 4);
      let second = explanationName[1].substring(4, 6);

      return `${year}.${month}.${date} ${hour}-${minute}-${second}`;
    } catch (err) {
      console.log("Exception occurred while generating date");
      return "";
    }
  }

  setActiveExplanation(event, explanationName) {
    this.setState({ activeExplanation: explanationName });
  }

  getActiveExplanation(event) {
    return this.state.activeExplanation;
  }

  handleDownload(event, explanation) {
    this.props.hideAppNotification();
    this.setState({
      downloadInProgress: true,
      activeExplanation: explanation,
    });
    console.log("download was called " + explanation);

    let config = {
      responseType: "blob",
      params: {
        explanation_name: explanation,
      },
    };
    axios
      .get(configs.explanationEndpoint, config)
      .then(
        function (response) {
          console.log(response);
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", `${explanation}`);
          document.body.appendChild(link);
          link.click();

          this.setState({
            snackbarMessage: "Explanation downloaded successfully!",
            snackbarType: "success",
            snackbarIsOpen: true,
            downloadInProgress: false,
            activeExplanation: undefined,
          });
        }.bind(this)
      )
      .catch(
        function (error) {
          console.log(error);
          let notifyTitle = "Explanation Error";
          let notifyBody = `An unknown error occurred while attempting to download the explanation specified (${explanation}). Please try again a bit later.`;
          let snackbarMessage =
            "An unknown error occurred while downloading the explanation";
          let snackbarType = "error";

          if (error instanceof CanceledError) {
            notifyBody = "Explanation Download Request Aborted!";
            snackbarMessage = notifyBody;
            snackbarType = "warning";
          } else if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            notifyBody = "Failed to obtain a valid explanation status";
            snackbarMessage = notifyBody;
          } else if (error.request) {
            // The request was made but no response was received
            console.log(error.request);
            notifyBody = "Server did not respond";
            snackbarMessage = notifyBody;
          } else {
            // Something happened in setting up the request that triggered an Error
            console.log("Error:", error.message);
            notifyBody = "Explanation download request failed";
            snackbarMessage = notifyBody;
          }
          console.log(error.config);

          this.setState({
            snackbarMessage: snackbarMessage,
            snackbarType: snackbarType,
            snackbarIsOpen: true,
            downloadInProgress: false,
            activeExplanation: undefined,
          });

          this.props.scrollToTop();
          this.props.showAppNotification(notifyTitle, notifyBody);
        }.bind(this)
      );
  }

  handleVisualize(event, explanation) {
    this.props.hideAppNotification();
    this.setState({
      activeExplanation: explanation,
      visualizeInProgress: true,
      activeVisualization: undefined,
    });
    console.log("download was called " + explanation);

    let config = {
      responseType: "json",
      params: {
        explanation_name: explanation,
      },
    };
    axios
      .get(configs.visualizationEndpoint, config)
      .then(
        function (response) {
          console.log(response);
          if (response.data.status !== undefined) {
            if (response.data.status === "success") {
              this.setState({
                snackbarMessage: "Visualization data received!",
                snackbarType: "success",
                snackbarIsOpen: true,
                visualizeInProgress: false,
                activeVisualization: JSON.parse(response.data.explanation),
                activeExplanation: undefined,
              });
              this.setState({ drawerIsOpen: true });
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
          let notifyTitle = "Explanation Error";
          let notifyBody = `An unknown error occurred while attempting to visualize the explanation specified (${explanation}). Please try again a bit later.`;
          let snackbarMessage =
            "An unknown error occurred while visualizing the explanation";
          let snackbarType = "error";

          if (error instanceof CanceledError) {
            notifyBody = "Visualization Request Aborted!";
            snackbarMessage = notifyBody;
            snackbarType = "warning";
          } else if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            notifyBody = "Failed to obtain a valid visualization status";
            snackbarMessage = notifyBody;
          } else if (error.request) {
            // The request was made but no response was received
            console.log(error.request);
            notifyBody = "Server did not respond";
            snackbarMessage = notifyBody;
          } else {
            // Something happened in setting up the request that triggered an Error
            console.log("Error:", error.message);
            notifyBody = "Visualization request failed";
            snackbarMessage = notifyBody;
          }
          console.log(error.config);

          this.setState({
            snackbarMessage: snackbarMessage,
            snackbarType: snackbarType,
            snackbarIsOpen: true,
            visualizeInProgress: false,
            activeExplanation: undefined,
            activeVisualization: undefined,
          });

          this.props.scrollToTop();
          this.props.showAppNotification(notifyTitle, notifyBody);
        }.bind(this)
      );
  }

  handleDelete(event, explanation) {
    this.props.hideAppNotification();
    this.setState({
      deleteInProgress: true,
      activeExplanation: explanation,
    });
    console.log("delete called " + explanation);

    let payload = {
      headers: {
        "Content-Type": "application/json",
      },
      data: {
        explanation_name: explanation,
      },
    };
    axios
      .delete(configs.explanationEndpoint, payload)
      .then(
        function (response) {
          console.log(response);
          if (response.data.status !== undefined) {
            if (response.data.status === "success") {
              this.setState({
                snackbarMessage: "Explanation deleted successfully!",
                snackbarType: "success",
                snackbarIsOpen: true,
                deleteInProgress: false,
                activeExplanation: undefined,
              });
              this.props.fetchExplanations();
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
          let notifyTitle = "Explanation Error";
          let notifyBody = `An unknown error occurred while attempting to delete the explanation specified (${explanation}). Please try again a bit later.`;
          let snackbarMessage =
            "An unknown error occurred while deleting the explanation";
          let snackbarType = "error";

          if (error instanceof CanceledError) {
            notifyBody = "Explanation Delete Request Aborted!";
            snackbarMessage = notifyBody;
            snackbarType = "warning";
          } else if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            notifyBody = "Failed to obtain a valid explanation status";
            snackbarMessage = notifyBody;
          } else if (error.request) {
            // The request was made but no response was received
            console.log(error.request);
            notifyBody = "Server did not respond";
            snackbarMessage = notifyBody;
          } else {
            // Something happened in setting up the request that triggered an Error
            console.log("Error:", error.message);
            notifyBody = "Explanation delete request failed";
            snackbarMessage = notifyBody;
          }
          console.log(error.config);

          this.setState({
            snackbarMessage: snackbarMessage,
            snackbarType: snackbarType,
            snackbarIsOpen: true,
            deleteInProgress: false,
            activeExplanation: undefined,
          });

          this.props.scrollToTop();
          this.props.showAppNotification(notifyTitle, notifyBody);
        }.bind(this)
      );
  }

  render() {
    return (
      <>
        <List sx={{ width: "100%" }} className="app-model-list" component="nav">
          <Divider component="li" variant="fullWidth" />
          {this.props.explanationList === undefined ? (
            <div className="p-3">
              Currently there are no Explanations Available
            </div>
          ) : (
            <ExplanationPaginator
              explanationList={this.props.explanationList}
              generateExplanationDate={this.generateExplanationDate}
              generateModalId={this.generateModalId}
              handleDelete={this.handleDelete}
              handleDownload={this.handleDownload}
              handleVisualize={this.handleVisualize}
              originChip={false}
              perPageItems={4}
            />
          )}
        </List>
        <Drawer
          anchor="right"
          open={this.state.drawerIsOpen}
          onClose={(e) => {
            this.handleDrawerClose(e);
          }}
          PaperProps={{ style: { width: "80%" } }}
          className={`app-explanation-drawer`}
        >
          <DialogTitle>
            <Box className="modal-header" style={{ border: "none" }}>
              <h5 className="modal-title">Explanation</h5>
              <button
                type="button"
                className="btn-close btn-close-white"
                onClick={(e) => {
                  this.handleDrawerClose(e);
                }}
              />
            </Box>
          </DialogTitle>
          {this.state.activeVisualization === undefined ? (
            <div className="w-100">
              Currently there are no generated explanation
            </div>
          ) : (
            <div className="w-100 row mt-4 pt-4 mb-0 model-common justify-content-center">
              <Box className="col-8 col-lg-8">
                <ExplanationDetails data={this.state.activeVisualization} />
                <GlobalExplanation
                  color="purple"
                  data={this.state.activeVisualization}
                />
                <DualExplanation
                  color="green"
                  data={this.state.activeVisualization}
                />
              </Box>
            </div>
          )}
        </Drawer>
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
