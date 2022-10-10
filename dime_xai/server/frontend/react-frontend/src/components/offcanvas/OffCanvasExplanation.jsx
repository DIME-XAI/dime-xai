import { Box } from "@mui/material";
import React, { Component } from "react";
import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";

const Alert = React.forwardRef((props, ref) => (
  <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />
));

export default class OffCanvasExplanation extends Component {
  constructor(props) {
    super(props);
    this.state = {
      snackbarIsOpen: false,
      snackbarMessage: "",
      snackbarType: "success",
      fetchInProgress: false,
    };

    this.handleFetch = this.handleFetch.bind(this);
    this.handleSnackbarClose = this.handleSnackbarClose.bind(this);
  }

  handleSnackbarClose(event) {
    this.setState({ snackbarIsOpen: false });
  }

  handleFetch(event) {}

  render() {
    return (
      <>
        <Box
          className="offcanvas offcanvas-end .offcanvas-lg container-bg-custom material-matt-black rounded-0 quick-instructions-offcanvas"
          data-bs-scroll="true"
          tabIndex="-1"
          id="dime-explanation-canvas"
          aria-labelledby="offcanvasWithBothOptionsLabel"
          sx={{ width: this.props.width }}
        >
          <Box className="offcanvas-header">
            <h5 className="offcanvas-title" id="offcanvasWithBothOptionsLabel">
              Explanation
            </h5>
            <button
              type="button"
              className="btn-close btn-close-white"
              data-bs-dismiss="offcanvas"
              aria-label="Close"
            ></button>
          </Box>
          <Box className="offcanvas-body scroll-hidden">
            <Box className="row align-items-md-stretch">
              <Box className="h-100 p-5 shadow material-blue">
                <h2>Dime Server Instructions</h2>
                <p>Generates DIET Explanations for Rasa.</p>
                <p>
                  This version of DIME Server supports Rasa 2.8.X. models only.
                </p>
                <p>Sample Config[]</p>
              </Box>
              {/* <Chip
            label="Generated"
            color="success"
            className="material-green" /> */}
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
