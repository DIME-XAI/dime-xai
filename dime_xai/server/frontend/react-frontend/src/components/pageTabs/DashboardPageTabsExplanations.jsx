import React, { Component } from "react";
import ExplanationsTab from "./ExplanationsTab";
import ConfigTab from "./ConfigTab";
import { Box, Button } from "@mui/material";

export default class DashboardPageTabsExplanations extends Component {
  constructor(props) {
    super(props);

    this.configTab = React.createRef();
    this.handleConfigTab = this.handleConfigTab.bind(this);
  }

  handleConfigTab(event) {
    this.configTab.current.click();
  }

  render() {
    return (
      <>
        <Box className="row align-items-md-stretch">
          <Box className="p-3 shadow-sm container-middle container-bg">
            <ul className="nav nav-tabs" id="myTab" role="tablist">
              <li className="nav-item" role="presentation">
                <Button
                  className="nav-link active app-tab"
                  id="exp-tab"
                  data-bs-toggle="tab"
                  data-bs-target="#exp-tab-pane"
                  type="button"
                  role="tab"
                  aria-controls="exp-tab-pane"
                  aria-selected="true"
                  variant="outlined"
                  sx={{
                    border: "none !important",
                    "&:hover": { border: "none" },
                  }}
                >
                  Explanations
                </Button>
              </li>
              <li className="nav-item" role="presentation">
                <Button
                  className="nav-link app-tab"
                  id="config-tab"
                  data-bs-toggle="tab"
                  data-bs-target="#config-tab-pane"
                  type="button"
                  role="tab"
                  aria-controls="config-tab-pane"
                  aria-selected="false"
                  variant="outlined"
                  sx={{
                    border: "none !important",
                    "&:hover": { border: "none" },
                  }}
                  ref={this.configTab}
                >
                  Configurations
                </Button>
              </li>
            </ul>
            <Box className="tab-content" id="myTabContent">
              <ExplanationsTab
                appConfigs={this.props.appConfigs}
                fetchStats={this.props.fetchStats}
                handleConfigTab={this.handleConfigTab}
                showAppNotification={this.props.showAppNotification}
                hideAppNotification={this.props.hideAppNotification}
                scrollToTop={this.props.scrollToTop}
              />
              <ConfigTab
                appConfigs={this.props.appConfigs}
                secureUrl={this.props.secureUrl}
                showAppNotification={this.props.showAppNotification}
                hideAppNotification={this.props.hideAppNotification}
                scrollToTop={this.props.scrollToTop}
                fetchStats={this.props.fetchStats}
                fetchConfigs={this.props.fetchConfigs}
              />
            </Box>
          </Box>
        </Box>
      </>
    );
  }
}
