import { Box } from "@mui/material";
import React, { Component } from "react";
import ExplanationList from "./ExplanationList";

export default class ExplanationsContainer extends Component {
  render() {
    return (
      <>
        <Box className="row align-items-md-stretch p-0 container-middle container-bg overflow-hidden">
          <Box className="shadow-sm p-0">
            <ExplanationList
              showAppNotification={this.props.showAppNotification}
              hideAppNotification={this.props.hideAppNotification}
              scrollToTop={this.props.scrollToTop}
              explanationList={this.props.explanationList}
              fetchExplanations={this.props.fetchExplanations}
            />
          </Box>
        </Box>
      </>
    );
  }
}
