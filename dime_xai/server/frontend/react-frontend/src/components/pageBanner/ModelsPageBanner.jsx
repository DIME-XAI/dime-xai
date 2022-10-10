import { Box } from "@mui/material";
import React, { Component } from "react";
import AppTile from "./AppTile";

export default class ModelsPageBanner extends Component {
  constructor(props) {
    super(props);
    this.state = {
      modelsListState: false,
    };

    this.showModelList = this.showModelList.bind(this);
  }

  showModelList(state) {
    this.setState({ modelsListState: state });
  }

  render() {
    return (
      <>
        <Box
          className="row row-cols-1 row-cols-lg-1"
          sx={{ marginY: 2, marginBottom: 3 }}
        >
          <AppTile
            bgcolor=""
            align="justify-content-start"
            margin="me-0 me-lg-0"
            icon="view_in_ar"
            iconColor="material-pink-f"
            count=""
            title="Conversational AI Models"
            content="Already trained conversational AI models can be found here. Let's you clean up the mess and only keep the models that performs the best."
            button={{
              button: false,
            }}
            customButton=""
          />
        </Box>
      </>
    );
  }
}
