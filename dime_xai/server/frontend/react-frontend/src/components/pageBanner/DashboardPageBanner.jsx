import { Box } from "@mui/material";
import React, { Component } from "react";
import { configs } from "../../configs";
import AppTile from "./AppTile";

export default class DashboardPageBanner extends Component {
  render() {
    return (
      <>
        <Box
          className="row row-cols-1 row-cols-lg-3"
          justifyContent="space-between"
          sx={{ marginY: 2 }}
        >
          <AppTile
            bgcolor=""
            spacing="pe-0 pe-lg-2 pb-2 pb-lg-0"
            icon="view_in_ar"
            iconColor="material-pink-f"
            count={
              this.props.stats === undefined ? "" : this.props.stats.models
            }
            title={
              this.props.stats === undefined
                ? " Models"
                : this.props.stats.models === 1
                ? " Model"
                : " Models"
            }
            content="To train a DIME compatible conversational AI model, 
            enable DIET classifier and train a new model beforehand."
            button={{
              button: true,
              buttonText: "View All Models",
              buttonType: "app-button-steel",
              externalLink: false,
              link: "/models",
            }}
            customButton=""
            // customButton={{
            //   buttonText: "View All Models",
            //   buttonType: "app-button-steel",
            //   onClickHandler: this.showModelList
            // }}
          />

          <AppTile
            bgcolor=""
            spacing="px-0 px-lg-3 py-2 py-lg-0"
            icon="psychology_alt"
            iconColor="material-steel-f"
            count={
              this.props.stats === undefined
                ? ""
                : this.props.stats.explanations
            }
            title={
              this.props.stats === undefined
                ? " Explanations"
                : this.props.stats.explanations === 1
                ? " Explanation"
                : " Explanations"
            }
            content="All previously generated explanations can be easily 
            managed, quickly visualized, exported, or imported here."
            button={{
              button: true,
              buttonText: "Manage Explanations",
              buttonType: "app-button-steel",
              externalLink: false,
              link: "/explanations",
            }}
            customButton=""
          />

          <AppTile
            bgcolor=""
            spacing="ps-0 ps-lg-2 pt-2 pt-lg-0"
            icon="quickreply"
            iconColor="material-green-f"
            count=""
            title=" Docs"
            content="Refer the official Kolloqui docs or DIME docs to get familiar 
            with the DIME server, DIME CLI and how it all works."
            button={{
              button: true,
              buttonText: "Explore Docs",
              buttonType: "app-button-steel",
              externalLink: true,
              link: `${configs.dimeDocsHost}`,
            }}
            customButton=""
          />
        </Box>
      </>
    );
  }
}
