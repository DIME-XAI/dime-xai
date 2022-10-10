import React, { Component } from "react";
import "./AppLoader.css";
import dimeGray from "./dimeGray.png";
import { configs } from "../../configs";
import { motion } from "framer-motion";
import MuiAlert from "@mui/material/Alert";
import { Container, LinearProgress, Snackbar, Stack } from "@mui/material";

const Alert = React.forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

export default class AppLoader extends Component {
  constructor(props) {
    super(props);
    this.state = {
      snackbarIsOpen: true,
    };

    this.handleClose = this.handleClose.bind(this);
  }

  handleClose(event) {
    this.setState({ snackbarIsOpen: false });
  }

  render() {
    return (
      <div className="app-config-loader">
        <header className="app-config-loader-header">
          <div>
            <Stack sx={{ width: "100%", color: "grey.500" }} spacing={2}>
              <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5, ease: "backInOut" }}
              >
                <img
                  src={dimeGray}
                  className="app-config-loader-logo"
                  alt="logo"
                />
              </motion.div>
              {this.props.status ? (
                <Container>
                  <LinearProgress
                    color="inherit"
                    className="mx-4"
                    sx={{ borderRadius: 2 }}
                  />
                </Container>
              ) : (
                <>
                  <motion.h6
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.6 }}
                  >
                    {`No configs found. `}
                    <span
                      className={"material-red-f"}
                      role={"button"}
                      onClick={this.props.fetchConfigs}
                    >
                      Retry
                    </span>
                  </motion.h6>
                  <Snackbar
                    open={this.state.snackbarIsOpen}
                    autoHideDuration={9000}
                    onClose={this.handleClose}
                    anchorOrigin={{
                      vertical: `${configs.snackbarVerticalPosition}`,
                      horizontal: `${configs.snackbarHorizontalPostion}`,
                    }}
                  >
                    <Alert
                      onClose={this.handleClose}
                      severity="error"
                      sx={{ width: "100%" }}
                    >
                      {`Failed to retrieve server configs.`}
                    </Alert>
                  </Snackbar>
                </>
              )}
            </Stack>
          </div>
        </header>
      </div>
    );
  }
}
