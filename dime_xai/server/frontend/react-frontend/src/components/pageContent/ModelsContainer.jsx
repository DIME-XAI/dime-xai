import { Box } from "@mui/material";
import React, { Component } from "react";
import ModelList from "./ModelList";

export default class ModelsContainer extends Component {
  render() {
    return (
      <>
        <Box className="row align-items-md-stretch p-0 container-middle container-bg overflow-hidden">
          <Box className="shadow-sm p-0">
            <ModelList
              appConfigs={this.props.appConfigs}
              showAppNotification={this.props.showAppNotification}
              hideAppNotification={this.props.hideAppNotification}
              scrollToTop={this.props.scrollToTop}
            />
          </Box>
        </Box>
      </>
    );
  }
}
